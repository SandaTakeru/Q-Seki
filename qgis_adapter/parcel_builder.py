from __future__ import annotations

from decimal import Decimal
from typing import Any, List, Sequence, Tuple

try:
    from qgis.core import QgsExpression, QgsExpressionContextUtils, QgsProject
except ImportError:  # pragma: no cover - optional QGIS runtime only
    QgsExpression = None  # type: ignore
    QgsExpressionContextUtils = None  # type: ignore
    QgsProject = None  # type: ignore


def layer_by_name_or_id(layer_ref: str, project: Any | None = None) -> Any:
    """レイヤ名またはレイヤIDからレイヤを解決する。"""
    if QgsProject is None:
        raise RuntimeError("QGIS runtime is required for layer lookup.")
    project_obj = project or QgsProject.instance()
    if layer_ref in project_obj.mapLayers():
        return project_obj.mapLayers()[layer_ref]
    for layer in project_obj.mapLayers().values():
        if layer.name() == layer_ref:
            return layer
    raise ValueError(f"Layer not found: {layer_ref!r}")


def _feature_matches_filter(feature: Any, expression_text: str) -> bool:
    """QGIS の式フィルタ文字列を適用する。"""
    if not expression_text:
        return True
    if QgsExpression is None or QgsExpressionContextUtils is None:
        return True
    expression = QgsExpression(expression_text)
    context = QgsExpressionContextUtils.createFeatureBasedContext(feature)
    return bool(expression.evaluate(context))


def resolve_feature_selection(layer: Any, feature_filter: str, atlas_feature_id: Any | None = None) -> List[Any]:
    """指定方法に応じて対象地物を解決する。"""
    if not feature_filter:
        return list(layer.getFeatures())

    if feature_filter == "@atlas_featureid":
        if atlas_feature_id is None:
            return []
        return [layer.getFeature(atlas_feature_id)]

    if feature_filter.strip().startswith("@atlas_featureid"):
        if atlas_feature_id is None:
            return []
        return [layer.getFeature(atlas_feature_id)]

    if isinstance(feature_filter, str) and "," in feature_filter:
        ids = [item.strip() for item in feature_filter.split(",") if item.strip()]
        matches: List[Any] = []
        for feature_id in ids:
            if feature_id.isdigit():
                try:
                    feature = layer.getFeature(int(feature_id))
                except Exception:
                    continue
                if feature.isValid():
                    matches.append(feature)
        if matches:
            return matches

    return [feature for feature in layer.getFeatures() if _feature_matches_filter(feature, feature_filter)]


def feature_label(feature: Any, label_field: str | None = None) -> str:
    """地物の見出し用ラベルを返す。デフォルトは「地番」だが、任意属性に変更可能。"""
    if feature is None:
        return "未選択"

    fields = feature.fields()
    candidate_names: List[str] = []
    if label_field:
        candidate_names.append(label_field)
    candidate_names.extend(["地番", "地番1", "地番2", "地目", "id", "fid", "label", "name"])

    for field_name in candidate_names:
        idx = fields.indexFromName(field_name)
        if idx >= 0:
            value = feature[field_name]
            if value is not None and str(value).strip() != "":
                return str(value)

    for field_name in fields.names():
        if field_name and field_name.lower() in {"地番", "地番1", "地番2", "label", "name", "id", "fid"}:
            value = feature[field_name]
            if value is not None and str(value).strip() != "":
                return str(value)

    return str(feature.id())


def geometry_to_parts(geometry: Any, start: str = "north") -> List[List[Tuple[Decimal, Decimal]]]:
    """QGIS のジオメトリを外側/内側リングに分離して座標リストに変換する。"""
    if geometry is None:
        return []

    if geometry.isMultipart():
        results: List[List[Tuple[Decimal, Decimal]]] = []
        for part in geometry.asGeometryCollection():
            results.extend(geometry_to_parts(part, start=start))
        return results

    polygon = geometry.asPolygon()
    if not polygon:
        return []

    parts: List[List[Tuple[Decimal, Decimal]]] = []
    parts.append([(Decimal(str(x)), Decimal(str(y))) for x, y in polygon[0]])
    for hole in polygon[1:]:
        parts.append([(Decimal(str(x)), Decimal(str(y))) for x, y in hole])
    return parts


def find_matching_point_attributes(
    vertices: Sequence[Tuple[Decimal, Decimal]],
    point_layer: Any,
    name_field: str,
    marker_field: str | None = None,
    tolerance: Decimal = Decimal("0.0005"),
) -> tuple[List[str], List[str], List[str]]:
    """各頂点に最も近いポイントの点名と境界標タイプを割り当てる。"""
    names: List[str] = []
    markers: List[str] = []
    warnings: List[str] = []

    point_features = list(point_layer.getFeatures())

    for point in vertices:
        best_name = "?"
        best_marker = ""
        best_distance: Decimal | None = None
        for candidate in point_features:
            geom = candidate.geometry()
            if geom is None or geom.isEmpty():
                continue
            if geom.type() != 0:
                continue
            cx, cy = geom.asPoint().x(), geom.asPoint().y()
            dx = Decimal(str(cx)) - point[0]
            dy = Decimal(str(cy)) - point[1]
            distance = (dx * dx + dy * dy).sqrt()
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_name = str(candidate[name_field]) if name_field in candidate.fields().names() else "?"
                if marker_field and marker_field in candidate.fields().names():
                    value = candidate[marker_field]
                    best_marker = "" if value is None else str(value)
                else:
                    best_marker = ""
        if best_distance is None or best_distance > tolerance:
            warnings.append(f"点 {point} に一致する {name_field} が見つかりません")
            names.append("?")
            markers.append("")
        else:
            names.append(best_name)
            markers.append(best_marker)
    return names, markers, warnings


def find_matching_point_names(
    vertices: Sequence[Tuple[Decimal, Decimal]],
    point_layer: Any,
    name_field: str,
    tolerance: Decimal = Decimal("0.0005"),
) -> tuple[List[str], List[str]]:
    """後方互換用: 点名だけを返す。"""
    names, _, warnings = find_matching_point_attributes(vertices, point_layer, name_field, marker_field=None, tolerance=tolerance)
    return names, warnings


def build_parcel_requests(
    polygon_layer: Any,
    feature_filter: str,
    point_layer: Any,
    name_field: str,
    tolerance: Decimal = Decimal("0.0005"),
    start: str = "north",
) -> List[dict[str, Any]]:
    """要求される地物ごとの求積入力を生成する。"""
    features = resolve_feature_selection(polygon_layer, feature_filter)
    requests: List[dict[str, Any]] = []
    for feature in features:
        geometry = feature.geometry()
        if geometry is None or geometry.isEmpty():
            continue
        parts = geometry_to_parts(geometry, start=start)
        labels = feature_label(feature)
        names: List[str] = []
        warnings: List[str] = []
        if parts:
            names, warnings = find_matching_point_names(parts[0], point_layer, name_field, tolerance=tolerance)
        requests.append(
            {
                "label": labels,
                "parts": parts,
                "point_names": names,
                "warnings": warnings,
            }
        )
    return requests
