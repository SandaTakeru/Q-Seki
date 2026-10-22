from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import re
import unicodedata
from typing import Any, Sequence

try:
    from qgis.core import qgsfunction
except ImportError:  # pragma: no cover
    def qgsfunction(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from .core.geometry import normalize_ring
    from .core.rounding import area_round
    from .core.report import ParcelReport, PartReport, ReportBundle, VertexRow, build_html_report
    from .qgis_adapter.parcel_builder import (
        feature_label,
        find_matching_point_attributes,
        geometry_to_parts,
        layer_by_name_or_id,
        resolve_feature_selection,
    )
except ImportError:  # pragma: no cover
    from core.geometry import normalize_ring
    from core.rounding import area_round
    from core.report import ParcelReport, PartReport, ReportBundle, VertexRow, build_html_report
    from qgis_adapter.parcel_builder import (
        feature_label,
        find_matching_point_attributes,
        geometry_to_parts,
        layer_by_name_or_id,
        resolve_feature_selection,
    )


def _qgis_string(value: Any) -> str:
    """QGIS の文字列リテラルへ安全に変換する。"""
    if value is None:
        return "''"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{text}'"


def _qgis_identifier(value: str) -> str:
    """QGIS 式の識別子（フィールド名）として安全にエスケープする。"""
    return f'"{str(value).replace("\"", "\"\"")}"'


def _qgis_array(values: Sequence[Any]) -> str:
    """QGIS の array(...) リテラルを返す。"""
    return f"array({', '.join(_qgis_string(v) for v in values)})"


_EXPRESSION_TOKEN_RE = re.compile(r"[@=<>!()\[\]{}]|\band\b|\bor\b|\bnot\b", re.IGNORECASE)


def _is_atlas_feature_reference(text: str) -> bool:
    """@atlas_featureid 参照かどうかを判定する。"""
    return text in {"@atlas_featureid"} or text.startswith("@atlas_featureid")


def _looks_like_qgis_expression(text: str) -> bool:
    """入力文字列が QGIS 式らしい構文を含むか判定する。"""
    return bool(_EXPRESSION_TOKEN_RE.search(text))


def _build_feature_filter_expression(feature_filter: Any, label_field: str) -> str:
    """地番値リストまたは既存式を、resolve_feature_selection 用の式へ正規化する。"""
    if feature_filter is None:
        return ""

    if isinstance(feature_filter, (list, tuple, set)):
        values = [str(v).strip() for v in feature_filter if str(v).strip()]
        if not values:
            return ""
        return f"{_qgis_identifier(label_field)} IN ({', '.join(_qgis_string(v) for v in values)})"

    text = str(feature_filter).strip()
    if not text:
        return ""

    if _is_atlas_feature_reference(text):
        return text

    if _looks_like_qgis_expression(text):
        return text

    # 「12-1,12-2」のようなカンマ区切りを地番リストとして扱う。
    if "," in text:
        values = [v.strip() for v in text.split(",") if v.strip()]
        if values:
            return f"{_qgis_identifier(label_field)} IN ({', '.join(_qgis_string(v) for v in values)})"

    # 単一値は地番属性への一致条件として扱う。
    return f"{_qgis_identifier(label_field)} = {_qgis_string(text)}"


def _normalize_chiban_text(value: Any) -> str:
    """地番比較向けに文字列を正規化する（ダッシュ類を半角ハイフンへ統一）。"""
    text = str(value).strip()
    dash_variants = {
        ord('−'): '-',  # minus sign
        ord('ー'): '-',  # katakana-hiragana prolonged sound mark
        ord('―'): '-',  # horizontal bar
        ord('‐'): '-',  # hyphen
        ord('‑'): '-',  # non-breaking hyphen
        ord('‒'): '-',  # figure dash
        ord('–'): '-',  # en dash
        ord('—'): '-',  # em dash
        ord('－'): '-',  # full-width hyphen-minus
    }
    return text.translate(dash_variants)


def _split_filter_values(feature_filter: Any) -> list[str]:
    """単純な地番フィルタ入力を値リストへ変換する。"""
    if feature_filter is None:
        return []
    if isinstance(feature_filter, (list, tuple, set)):
        return [str(v).strip() for v in feature_filter if str(v).strip()]

    text = str(feature_filter).strip()
    if not text:
        return []
    if ',' in text:
        return [v.strip() for v in text.split(',') if v.strip()]
    return [text]


def _fallback_filter_by_label_values(layer: Any, label_field: str, feature_filter: Any) -> list[Any]:
    """式フィルタで0件だった場合のフォールバック（地番値の正規化比較）。"""
    wanted = {_normalize_chiban_text(v) for v in _split_filter_values(feature_filter)}
    if not wanted:
        return []

    matches: list[Any] = []
    for feature_obj in layer.getFeatures():
        try:
            field_value = feature_obj[label_field]
        except Exception:
            continue
        if field_value is None:
            continue
        if _normalize_chiban_text(field_value) in wanted:
            matches.append(feature_obj)
    return matches


def _resolve_label_field_name(layer: Any, label_field: str | None) -> str | None:
    """レイヤ上に存在する地番属性名を解決する。"""
    try:
        qfields = list(layer.fields())
    except Exception:
        return None

    def _norm(text: Any) -> str:
        return unicodedata.normalize('NFKC', str(text)).strip().casefold()

    # 実フィールド名・表示名(エイリアス)の両方で解決できるようにする
    field_names: list[str] = []
    normalized_name_map: dict[str, str] = {}
    normalized_alias_map: dict[str, str] = {}

    for f in qfields:
        try:
            name = str(f.name())
        except Exception:
            continue
        field_names.append(name)
        normalized_name_map[_norm(name)] = name

        alias_value = ''
        try:
            alias_attr = getattr(f, 'alias', None)
            alias_value = alias_attr() if callable(alias_attr) else (alias_attr or '')
        except Exception:
            alias_value = ''
        if alias_value:
            normalized_alias_map[_norm(alias_value)] = name

    candidates: list[str] = []
    if label_field:
        candidates.append(str(label_field))
    candidates.extend(['地番', '地番1', '地番2'])

    for candidate in candidates:
        if candidate in field_names:
            return candidate

    normalized_map = {str(name).strip(): name for name in field_names}
    for candidate in candidates:
        key = str(candidate).strip()
        if key in normalized_map:
            return normalized_map[key]

    # Unicode 揺れ・大小文字・全半角・エイリアス対応
    for candidate in candidates:
        key = _norm(candidate)
        if key in normalized_name_map:
            return normalized_name_map[key]
        if key in normalized_alias_map:
            return normalized_alias_map[key]

    return None


def _is_simple_filter_input(feature_filter: Any) -> bool:
    """式ではなく地番値指定（単一/複数）かどうか。"""
    if feature_filter is None:
        return True
    if isinstance(feature_filter, (list, tuple, set)):
        return True
    text = str(feature_filter).strip()
    if not text:
        return True
    if _is_atlas_feature_reference(text):
        return False
    return not _looks_like_qgis_expression(text)


def build_kyuseki_expression(
    polygon_layer: Any,
    label_field: str = "地番",
    feature_filter: Any = "",
    point_layer: Any = None,
    name_field: str = "点名",
    marker_field: str | None = None,
    full_precision: bool = False,
    coord_digits: int = 3,
    area_digits: int = 2,
    column_count: int = 1,
    show_total_table: bool = False,
    show_tsubo: bool = False,
    start: str = 'north',
    tolerance: float = 0.0005,
) -> str:
    """`kyuseki_html()` 呼び出し式を安全に組み立てて返す。"""
    polygon_name = getattr(polygon_layer, 'name', lambda: str(polygon_layer))()
    if point_layer is None:
        point_name = ''
    else:
        point_name = getattr(point_layer, 'name', lambda: str(point_layer))()

    if isinstance(feature_filter, (list, tuple, set)):
        filter_arg = _qgis_array([str(v) for v in feature_filter if str(v).strip()])
    else:
        filter_arg = _qgis_string(feature_filter)

    parts = [
        _qgis_string(polygon_name),
        _qgis_string(label_field),
        filter_arg,
        _qgis_string(point_name),
        _qgis_string(name_field),
        _qgis_string(marker_field or ''),
        'true' if full_precision else 'false',
        str(coord_digits),
        str(area_digits),
        str(column_count),
        'true' if show_total_table else 'false',
        'true' if show_tsubo else 'false',
        _qgis_string(start),
        str(tolerance),
    ]
    return f"kyuseki_html({', '.join(parts)})"


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {'1', 'true', 'yes', 'on'}:
        return True
    if text in {'0', 'false', 'no', 'off'}:
        return False
    return default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return default


def _normalize_start_direction(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {'north', 'east', 'south', 'west'}:
        return text
    jp_to_en = {
        '北': 'north',
        '東': 'east',
        '南': 'south',
        '西': 'west',
    }
    return jp_to_en.get(str(value).strip(), 'north')


def _resolve_layer(layer_ref: Any) -> Any:
    """レイヤ名またはIDをQGISレイヤへ変換する。"""
    if layer_ref is None:
        raise ValueError("polygon_layer should not be null")
    if hasattr(layer_ref, "getFeatures"):
        return layer_ref
    return layer_by_name_or_id(str(layer_ref))


def _dedupe_ring_vertices(vertices: Sequence[tuple[Decimal, Decimal]]) -> list[tuple[Decimal, Decimal]]:
    """リング座標から重複点を除去する（順序は維持）。"""
    if not vertices:
        return []

    # 閉じリングの末尾重複（始点=終点）を除去
    points = list(vertices)
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]

    # 異常な重複点も除去（最初の出現のみ採用）
    deduped: list[tuple[Decimal, Decimal]] = []
    seen: set[tuple[Decimal, Decimal]] = set()
    for point in points:
        if point in seen:
            continue
        seen.add(point)
        deduped.append(point)

    return deduped


__all__ = ["build_kyuseki_expression"]


@qgsfunction(args='auto', group='Q積表', handlesnull=True)
def kyuseki_html(
    polygon_layer: Any,
    label_field: str = '地番',
    feature_filter: Any = '',
    point_layer: Any = None,
    name_field: str = '点名',
    marker_field: str = '境界標',
    full_precision: bool = False,
    coord_digits: int = 3,
    area_digits: int = 2,
    column_count: int = 1,
    show_total_table: bool = False,
    show_tsubo: bool = False,
    start: str = 'north',
    tolerance: float = 0.0005,
    feature: Any | None = None,
    parent: Any | None = None,
) -> str:
    """<p>kyuseki_html — 求積表（HTML）を生成</p>
<p>フィールド計算機・印刷レイアウト（ラベル/HTML）向けの関数です。</p>

<h3>Syntax</h3>
kyuseki_html(polygon_layer[, label_field][, feature_filter][, point_layer][, name_field][, marker_field][, full_precision][, coord_digits][, area_digits][, column_count][, show_total_table][, show_tsubo][, start][, tolerance])<br/>
[ ] は省略可能な引数です。</p>

<h3>Arguments</h3>
<ul>
<li><b>polygon_layer</b>: 対象土地ポリゴンレイヤ（名前 or ID）</li>
<li><b>label_field</b>: 地番名の属性名（既定: 地番）（省略可）</li>
<li><b>feature_filter</b>: フィルタ地番（単一値/カンマ区切り/配列/式）（省略可）</li>
<li><b>point_layer</b>: 対象座標ポイントレイヤ（名前 or ID）（省略可）</li>
<li><b>name_field</b>: 点名の属性名（既定: 点名）（省略可）</li>
<li><b>marker_field</b>: 境界標の種類の属性名（既定: 境界標）（省略可）</li>
<li><b>full_precision</b>: true でフル桁表示（coord_digits は無視）（既定: false）（省略可）</li>
<li><b>coord_digits</b>: full_precision=false 時の座標値の丸め後桁数（既定: 3）（省略可）</li>
<li><b>area_digits</b>: 地積の切り捨て表示桁数（既定: 2）（省略可）</li>
<li><b>column_count</b>: 表示列数（0/1 は縦1列、2以上で横方向に分割配置）（既定: 1）（省略可）</li>
<li><b>show_total_table</b>: 求積表最下部に合計表を表示するか（true/false）（既定: false）（省略可）</li>
<li><b>show_tsubo</b>: true で地積の下に坪換算値を表示（地積の切り捨て済み値を換算）（既定: false）（省略可）</li>
<li><b>start</b>: 頂点開始方向（north/east/south/west）（省略可）</li>
<li><b>tolerance</b>: 点名照合トレランス、ポリゴンの頂点とポイントの座標のズレ許容距離（既定 0.0005）（省略可）</li>
</ul>

<h3>Display rules</h3>
feature_filter は単一値、カンマ区切り、配列、QGIS 式、@atlas_featureid を受け付けます。<br/>
列見出しは (Xn+1-Xn-1)Yn です。<br/>
full_precision=false のとき、(Xn+1-Xn-1)Yn と倍面積は 2×coord_digits 桁、面積は 2×coord_digits+1 桁で表示します。<br/>
full_precision=true のとき、上記は丸めずフル桁表示し、見出しに「（フル桁）」を付与します。<br/>
地積は full_precision に関わらず area_digits 桁で常に切り捨て表示します。<br/>
穴開きポリゴンの「外郭-穴」は、外郭/穴の各パート行で計算された倍面積の合算を基準に、倍面積・面積・地積を算出します。<br/>
show_total_table=true の場合、最下部に「合計 / 面積の合計（full_precision=true のときは（フル桁）付き） / 地積の合計」の表を表示します。</p>
show_tsubo=true の場合、地積（切り捨て済み）を基準に換算した「地積（坪）」行を、地積の直下に表示します。</p>
column_count=0/1 は従来どおり縦1列、column_count=2 以上で地番ごとの表を横方向に分割配置します。</p>

<h3>Examples</h3>
kyuseki_html('境界', '地番', '12-1', '点名', '点名', '境界標')<br/>
kyuseki_html('境界', '地番', array('12-1','12-2'), '点名', '点名', '境界標', false, 3, 2, 3, true, true, 'north', 0.0005)</p>"""
    column_count = max(0, _as_int(column_count, 1))
    show_total_table = _as_bool(show_total_table, False)
    show_tsubo = _as_bool(show_tsubo, False)
    start = _normalize_start_direction(start)
    tolerance = _as_float(tolerance, 0.0005)

    if polygon_layer is None:
        return '地物レイヤが未指定です。'

    try:
        layer = _resolve_layer(polygon_layer)
    except Exception as exc:
        return f"地物レイヤを解決できません: {exc}"
    if layer.crs() is not None and getattr(layer.crs(), 'isGeographic', lambda: False)():
        return '地理座標系では求積表を作成できません。'

    point_layer_obj = None
    if point_layer is not None and str(point_layer).strip() != '':
        try:
            point_layer_obj = _resolve_layer(point_layer)
        except Exception as exc:
            return f"点名レイヤを解決できません: {exc}"
    resolved_label_field = _resolve_label_field_name(layer, label_field)
    effective_label_field = resolved_label_field or (str(label_field) if label_field else '地番')
    simple_filter = _is_simple_filter_input(feature_filter)

    if simple_filter and feature_filter not in (None, '') and resolved_label_field:
        features = _fallback_filter_by_label_values(layer, resolved_label_field, feature_filter)
    else:
        filter_expression = _build_feature_filter_expression(feature_filter, effective_label_field)
        atlas_feature_id = feature.id() if feature is not None and hasattr(feature, 'id') else None
        features = resolve_feature_selection(
            layer,
            filter_expression,
            atlas_feature_id=atlas_feature_id,
        )

    if not features and simple_filter and feature_filter not in (None, '') and resolved_label_field:
        # 念のため（将来の経路変更に備えた二重化）
        features = _fallback_filter_by_label_values(layer, resolved_label_field, feature_filter)
    if not features:
        return '対象地物がありません。'

    parcels: list[ParcelReport] = []
    total_area = Decimal('0')
    total_reference_area = Decimal('0')

    for feature in features:
        if feature is None:
            continue
        geom = feature.geometry()
        if geom is None or geom.isEmpty():
            continue
        rings = geometry_to_parts(geom, start=start)
        if not rings:
            continue

        parcel_parts: list[PartReport] = []
        parcel_total = Decimal('0')
        warnings: list[str] = []
        for idx, ring in enumerate(rings):
            vertices = normalize_ring(ring, start=start)
            if idx > 0:
                # 穴は時計回り（負の倍面積）
                vertices = list(reversed(vertices))

            vertices = _dedupe_ring_vertices(vertices)
            if len(vertices) < 3:
                warnings.append(f"リング{idx + 1}の有効頂点が不足しています")
                continue

            try:
                if point_layer_obj is None:
                    names = ['?'] * len(vertices)
                    markers = [''] * len(vertices)
                    name_warnings = []
                else:
                    names, markers, name_warnings = find_matching_point_attributes(
                        vertices,
                        point_layer_obj,
                        name_field,
                        marker_field=marker_field,
                        tolerance=Decimal(str(tolerance)),
                    )
            except Exception:
                names = ['?'] * len(vertices)
                markers = [''] * len(vertices)
                name_warnings = []
            if name_warnings:
                warnings.extend(name_warnings)

            rounded_vertices = [
                (
                    _rounded_coord(x, coord_digits, full_precision=full_precision),
                    _rounded_coord(y, coord_digits, full_precision=full_precision),
                )
                for x, y in vertices
            ]

            rows = []
            n = len(rounded_vertices)
            for i in range(n):
                east, north = rounded_vertices[i]
                prev_east, prev_north = rounded_vertices[(i - 1) % n]
                next_east, next_north = rounded_vertices[(i + 1) % n]
                delta_north = next_north - prev_north
                x_mul = east * delta_north
                name = names[i] if i < len(names) else '?'
                marker = markers[i] if i < len(markers) else ''
                rows.append(
                    VertexRow(
                        name=name,
                        x=north,
                        y=east,
                        delta_y=delta_north,
                        x_mul_delta_y=x_mul,
                        marker=marker,
                    )
                )

            rounded_total_x_mul = sum((row.x_mul_delta_y for row in rows), Decimal('0'))
            rounded_area_raw = rounded_total_x_mul / Decimal('2')
            rounded_area = area_round(rounded_area_raw, digits=area_digits)
            if idx == 0:
                parcel_total = rounded_area
            else:
                parcel_total += rounded_area
            twice_area = rounded_total_x_mul
            area = rounded_area

            parcel_parts.append(
                PartReport(
                    title='外郭' if idx == 0 else f'穴{idx}',
                    rows=rows,
                    twice_area=twice_area,
                    area=area,
                    is_hole=(idx > 0),
                )
            )

        parcel_reference_area = sum(
            (sum((Decimal(str(row.x_mul_delta_y)) for row in part.rows), Decimal('0')) for part in parcel_parts),
            Decimal('0'),
        )
        parcel_total = area_round(parcel_reference_area / Decimal('2'), digits=area_digits)

        total_area += parcel_total
        total_reference_area += parcel_reference_area
        parcels.append(
            ParcelReport(
                label=str(feature_label(feature, label_field=effective_label_field)),
                parts=parcel_parts,
                total_area=Decimal(str(parcel_total)),
                reference_area=Decimal(str(parcel_reference_area)),
                warnings=warnings,
            )
        )

    bundle = ReportBundle(parcels=parcels, total_area=total_area, total_reference_area=total_reference_area)
    return build_html_report(
        bundle,
        coord_digits=coord_digits,
        full_precision=full_precision,
        area_digits=area_digits,
        show_total_table=show_total_table,
        column_count=column_count,
        show_tsubo=show_tsubo,
    )


def _rounded_coord(value: Decimal | int | float | str, digits: int, full_precision: bool = False) -> Decimal:
    """実務上の丸め済み座標値を返す。"""
    if full_precision:
        return Decimal(str(value))
    quant = Decimal("1").scaleb(-digits)
    return Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)


__all__.append("kyuseki_html")
