from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Sequence

from .rounding import area_round


@dataclass
class VertexRow:
    name: str
    x: Decimal
    y: Decimal
    delta_y: Decimal
    x_mul_delta_y: Decimal
    marker: str = ""


@dataclass
class PartReport:
    title: str
    rows: List[VertexRow] = field(default_factory=list)
    twice_area: Decimal = Decimal("0")
    area: Decimal = Decimal("0")
    is_hole: bool = False
    warning: str | None = None


@dataclass
class ParcelReport:
    label: str
    parts: List[PartReport] = field(default_factory=list)
    total_area: Decimal = Decimal("0")
    reference_area: Decimal = Decimal("0")
    warnings: List[str] = field(default_factory=list)


@dataclass
class ReportBundle:
    parcels: List['ParcelReport'] = field(default_factory=list)
    total_area: Decimal = Decimal("0")
    total_reference_area: Decimal = Decimal("0")


def _coord_display(value: Decimal | int | float | str, digits: int = 3) -> str:
    quant = Decimal("1").scaleb(-digits)
    return format(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP), f".{digits}f")


def _coord_full_precision_display(value: Decimal | int | float | str, min_digits: int = 3) -> str:
    dec = Decimal(str(value))
    text = format(dec, "f")
    if "." not in text:
        if min_digits <= 0:
            return text
        return f"{text}.{('0' * min_digits)}"

    integer, fraction = text.split(".", 1)
    if len(fraction) < min_digits:
        fraction += "0" * (min_digits - len(fraction))
    return f"{integer}.{fraction}"


def _product_display(value: Decimal | int | float | str, digits: int = 6) -> str:
    quant = Decimal("1").scaleb(-digits)
    return format(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP), f".{digits}f")


def _product_full_precision_display(value: Decimal | int | float | str) -> str:
    dec = Decimal(str(value))
    text = format(dec, "f")
    return text


def _product_digits_from_coord_digits(coord_digits: int) -> int:
    return max(0, int(coord_digits) * 2)


def _half_area_digits_from_coord_digits(coord_digits: int) -> int:
    return _product_digits_from_coord_digits(coord_digits) + 1


def _area_display(value: Decimal | int | float | str, digits: int = 2) -> str:
    rounded = area_round(Decimal(str(value)), digits=digits)
    return format(rounded, f".{digits}f")


def _tsubo_display_from_truncated_area(value: Decimal | int | float | str, digits: int = 2) -> str:
    """切り捨て済み地積(㎡)を坪へ換算して表示文字列を返す。"""
    area_truncated = area_round(Decimal(str(value)), digits=digits)
    # 1 ㎡ = 121 / 400 坪
    tsubo = area_truncated * Decimal('121') / Decimal('400')
    tsubo_truncated = area_round(tsubo, digits=digits)
    return format(tsubo_truncated, f".{digits}f")


def format_row(row: VertexRow, coord_digits: int = 3, full_precision: bool = False) -> List[str]:
    """表示用の行を返す。座標は丸め済み値、積算は計算後の厳密値をそのまま用いる。"""
    signed_x = Decimal(str(row.x))
    signed_y = Decimal(str(row.y))
    x_mul = Decimal(str(row.x_mul_delta_y))
    marker = getattr(row, 'marker', '')
    x_text = _coord_full_precision_display(signed_x, min_digits=0) if full_precision else _coord_display(signed_x, digits=coord_digits)
    y_text = _coord_full_precision_display(signed_y, min_digits=0) if full_precision else _coord_display(signed_y, digits=coord_digits)
    product_digits = _product_digits_from_coord_digits(coord_digits)
    product_text = _product_full_precision_display(x_mul) if full_precision else _product_display(x_mul, digits=product_digits)
    return [
        row.name,
        x_text,
        y_text,
        product_text,
        marker,
    ]


def _deduplicate_closed_ring(rows: Sequence[VertexRow]) -> List[VertexRow]:
    """閉じたリングの重複座標を除去する。"""
    if len(rows) < 2:
        return list(rows)

    cleaned: List[VertexRow] = []
    for row in rows:
        if not cleaned:
            cleaned.append(row)
            continue
        prev = cleaned[-1]
        if row.x == prev.x and row.y == prev.y:
            continue
        cleaned.append(row)

    if len(cleaned) >= 2:
        first = cleaned[0]
        last = cleaned[-1]
        if first.x == last.x and first.y == last.y:
            cleaned.pop()

    return cleaned


def build_html_report(
    bundle: ReportBundle,
    coord_digits: int = 3,
    full_precision: bool = False,
    area_digits: int = 2,
    show_total_table: bool = True,
    column_count: int = 1,
    show_tsubo: bool = False,
) -> str:
    """ReportBundle から整形済みの HTML を返す。"""
    import html

    product_digits = _product_digits_from_coord_digits(coord_digits)
    half_area_digits = _half_area_digits_from_coord_digits(coord_digits)
    product_label = "倍面積（フル桁）" if full_precision else "倍面積"
    half_area_label = "面積（フル桁）" if full_precision else "面積"
    area_label = "地積（フル桁）" if full_precision else "地積"

    css = (
        "table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #333;padding:4px;vertical-align:middle;}"
        "th{text-align:center;background:#fff;}"
        "td{background:#fff;}"
        "th.section{background:#f0f0f0;text-align:center;font-weight:bold;}"
        "th.section.parcel-title{font-size:1.15em;font-weight:800;letter-spacing:0.02em;}"
        "th.colhead{background:#f0f0f0;text-align:center;font-weight:bold;}"
        "td.num{text-align:right;}"
        "td.center{text-align:center;}"
        ".summary{font-weight:bold;text-align:right;}"
        ".summary-value{text-align:left;padding-left:22%;white-space:nowrap;}"
        "tr.spacer td{border:none !important;background:transparent !important;padding:8px 0 !important;height:8px;}"
    )
    parts: list[str] = [
        f"<style>{css}</style>",
    ]

    def _parcel_rows(parcel: ParcelReport) -> list[str]:
        parcel_parts: list[str] = []

        def _append_column_header_row() -> None:
            parcel_parts.append(
                "<tr>"
                "<th class='colhead'>点名</th>"
                "<th class='colhead'>Xn</th>"
                "<th class='colhead'>Yn</th>"
                "<th class='colhead'>(Xn+1-Xn-1)Yn</th>"
                "<th class='colhead'>境界標</th>"
                "</tr>"
            )

        if len(parcel.parts) == 1:
            part = parcel.parts[0]
            rows = [format_row(r, coord_digits=coord_digits, full_precision=full_precision) for r in _deduplicate_closed_ring(part.rows)]
            total_x_mul = sum((Decimal(str(r.x_mul_delta_y)) for r in part.rows), Decimal('0'))
            title_text = f"{parcel.label} / 穴" if part.is_hole else f"{parcel.label}"

            parcel_parts.append(f"<tr><th colspan='5' class='section parcel-title'>{html.escape(title_text)}</th></tr>")
            _append_column_header_row()
            for row in rows:
                parcel_parts.append(f"<tr><td class='center'>{html.escape(str(row[0]))}</td><td class='num'>{html.escape(str(row[1]))}</td><td class='num'>{html.escape(str(row[2]))}</td><td class='num'>{html.escape(str(row[3]))}</td><td class='center'>{html.escape(str(row[4]))}</td></tr>")
            total_x_mul_text = _product_full_precision_display(total_x_mul) if full_precision else _product_display(total_x_mul, digits=product_digits)
            half_x_mul_text = _product_full_precision_display(total_x_mul / Decimal('2')) if full_precision else _product_display(total_x_mul / Decimal('2'), digits=half_area_digits)
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>{product_label}</td><td class='summary summary-value' colspan='2'>{total_x_mul_text}</td></tr>")
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>{half_area_label}</td><td class='summary summary-value' colspan='2'>{half_x_mul_text}</td></tr>")
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>{area_label}</td><td class='summary summary-value' colspan='2'>{_area_display(part.area, digits=area_digits)} ㎡</td></tr>")
            if show_tsubo:
                parcel_parts.append(f"<tr><td class='summary' colspan='3'>地積（坪）</td><td class='summary summary-value' colspan='2'>{_tsubo_display_from_truncated_area(part.area, digits=area_digits)} 坪</td></tr>")
            return parcel_parts

        outer = next((p for p in parcel.parts if not p.is_hole), None)
        holes = [p for p in parcel.parts if p.is_hole]
        part_twice_totals: list[Decimal] = []
        parcel_parts.append(f"<tr><th colspan='5' class='section parcel-title'>{html.escape(f'{parcel.label}')}</th></tr>")

        if outer is not None:
            outer_rows = [format_row(r, coord_digits=coord_digits, full_precision=full_precision) for r in _deduplicate_closed_ring(outer.rows)]
            outer_total = sum((Decimal(str(r.x_mul_delta_y)) for r in outer.rows), Decimal('0'))
            parcel_parts.append(f"<tr><th colspan='5' class='section'>{html.escape(f'{parcel.label}（外郭）')}</th></tr>")
            _append_column_header_row()
            for row in outer_rows:
                parcel_parts.append(f"<tr><td class='center'>{html.escape(str(row[0]))}</td><td class='num'>{html.escape(str(row[1]))}</td><td class='num'>{html.escape(str(row[2]))}</td><td class='num'>{html.escape(str(row[3]))}</td><td class='center'>{html.escape(str(row[4]))}</td></tr>")
            outer_total_text = _product_full_precision_display(outer_total) if full_precision else _product_display(outer_total, digits=product_digits)
            part_twice_totals.append(outer_total)
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>{product_label}</td><td class='summary summary-value' colspan='2'>{outer_total_text}</td></tr>")

        for index, hole in enumerate(holes, start=1):
            hole_rows = [format_row(r, coord_digits=coord_digits, full_precision=full_precision) for r in _deduplicate_closed_ring(hole.rows)]
            hole_total = sum((Decimal(str(r.x_mul_delta_y)) for r in hole.rows), Decimal('0'))
            parcel_parts.append(f"<tr><th colspan='5' class='section'>{html.escape(f'{parcel.label}（穴{index}）')}</th></tr>")
            _append_column_header_row()
            for row in hole_rows:
                parcel_parts.append(f"<tr><td class='center'>{html.escape(str(row[0]))}</td><td class='num'>{html.escape(str(row[1]))}</td><td class='num'>{html.escape(str(row[2]))}</td><td class='num'>{html.escape(str(row[3]))}</td><td class='center'>{html.escape(str(row[4]))}</td></tr>")
            hole_total_text = _product_full_precision_display(hole_total) if full_precision else _product_display(hole_total, digits=product_digits)
            part_twice_totals.append(hole_total)
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>{product_label}</td><td class='summary summary-value' colspan='2'>{hole_total_text}</td></tr>")

        total_twice = sum(part_twice_totals, Decimal('0'))
        total_half = total_twice / Decimal('2')
        total_area = area_round(total_half, digits=area_digits)
        parcel_parts.append(f"<tr><th colspan='5' class='section'>{html.escape(f'{parcel.label}（外郭-穴）')}</th></tr>")
        total_twice_text = _product_full_precision_display(total_twice) if full_precision else _product_display(total_twice, digits=product_digits)
        total_half_text = _product_full_precision_display(total_half) if full_precision else _product_display(total_half, digits=half_area_digits)
        parcel_parts.append(f"<tr><td class='summary' colspan='3'>{product_label}</td><td class='summary summary-value' colspan='2'>{total_twice_text}</td></tr>")
        parcel_parts.append(f"<tr><td class='summary' colspan='3'>{half_area_label}</td><td class='summary summary-value' colspan='2'>{total_half_text}</td></tr>")
        parcel_parts.append(f"<tr><td class='summary' colspan='3'>{area_label}</td><td class='summary summary-value' colspan='2'>{_area_display(total_area, digits=area_digits)} ㎡</td></tr>")
        if show_tsubo:
            parcel_parts.append(f"<tr><td class='summary' colspan='3'>地積（坪）</td><td class='summary summary-value' colspan='2'>{_tsubo_display_from_truncated_area(total_area, digits=area_digits)} 坪</td></tr>")
        return parcel_parts

    def _total_rows() -> list[str]:
        total_half_area = bundle.total_reference_area / Decimal('2')
        total_half_area_label = "面積の合計（フル桁）" if full_precision else "面積の合計"
        total_half_area_text = (
            _product_full_precision_display(total_half_area)
            if full_precision
            else _product_display(total_half_area, digits=half_area_digits)
        )
        return [
            "<tr><th colspan='5' class='section'>合計</th></tr>",
            f"<tr><td class='summary' colspan='3'>{html.escape(total_half_area_label)}</td><td class='summary summary-value' colspan='2'>{html.escape(total_half_area_text)} ㎡</td></tr>",
            f"<tr><td class='summary' colspan='3'>地積の合計</td><td class='summary summary-value' colspan='2'>{_area_display(bundle.total_area, digits=area_digits)} ㎡</td></tr>",
        ] + ([
            f"<tr><td class='summary' colspan='3'>地積の合計（坪）</td><td class='summary summary-value' colspan='2'>{_tsubo_display_from_truncated_area(bundle.total_area, digits=area_digits)} 坪</td></tr>",
        ] if show_tsubo else [])

    normalized_column_count = max(1, int(column_count))

    if normalized_column_count > 1:
        layout_css = (
            ".ksh-flow{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed;}"
            ".ksh-flow > tbody > tr > td.ksh-flow-cell{border:none !important;background:transparent !important;padding:0 6px 10px 6px;vertical-align:top;}"
            ".ksh-flow > tbody > tr > td.ksh-flow-cell:first-child{padding-left:0;}"
            ".ksh-flow > tbody > tr > td.ksh-flow-cell:last-child{padding-right:0;}"
            ".ksh-column{width:100%;}"
            ".ksh-empty{height:1px;}"
        )
        parts[0] = f"<style>{css}{layout_css}</style>"

        parcel_blocks: list[list[str]] = []
        for parcel in bundle.parcels:
            parcel_blocks.append(_parcel_rows(parcel))

        col_count = max(1, min(normalized_column_count, max(1, len(parcel_blocks))))

        total_block: list[str] | None = None
        if show_total_table:
            total_block = _total_rows()

        n = len(parcel_blocks)
        block_heights = [len(block) for block in parcel_blocks]
        prefix_heights = [0]
        for h in block_heights:
            prefix_heights.append(prefix_heights[-1] + h)

        total_block_height = len(total_block) if total_block is not None else 0

        def _segment_height(start: int, end: int) -> int:
            """parcel_blocks[start:end] を1列へ積んだときの推定高さ（空白行込み）。"""
            count = end - start
            if count <= 0:
                return 0
            rows_sum = prefix_heights[end] - prefix_heights[start]
            spacer_rows = count - 1
            return rows_sum + spacer_rows

        def _column_height(col_idx: int, start: int, end: int) -> int:
            """col_idx 列に start:end を置いた場合の推定高さ。"""
            base_h = _segment_height(start, end)
            is_last = (col_idx == col_count - 1)
            if is_last and total_block is not None:
                if end > start:
                    return base_h + 1 + total_block_height  # 合計ブロック前の空白行
                return total_block_height
            return base_h

        # 推定高さの二乗誤差最小化で、列ごとの区切り位置を最適化する。
        target_height = (prefix_heights[-1] + total_block_height + max(0, n - col_count)) / col_count
        inf = float('inf')
        dp = [[inf] * (n + 1) for _ in range(col_count + 1)]
        prev = [[-1] * (n + 1) for _ in range(col_count + 1)]
        dp[0][0] = 0.0

        for col_idx in range(1, col_count + 1):
            for end in range(0, n + 1):
                # n >= col_count なので各列に最低1ブロックを入れる制約をかける
                min_start = col_idx - 1
                max_start = end
                if n >= col_count:
                    max_start = min(max_start, end - 1)

                if min_start > max_start:
                    continue

                for start in range(min_start, max_start + 1):
                    if dp[col_idx - 1][start] == inf:
                        continue
                    if n >= col_count:
                        remaining_cols = col_count - col_idx
                        remaining_items = n - end
                        if remaining_items < remaining_cols:
                            continue

                    col_h = _column_height(col_idx - 1, start, end)
                    score = dp[col_idx - 1][start] + ((col_h - target_height) ** 2)
                    if score < dp[col_idx][end]:
                        dp[col_idx][end] = score
                        prev[col_idx][end] = start

        boundaries: list[int] = [0] * (col_count + 1)
        boundaries[col_count] = n
        cursor = n
        for col_idx in range(col_count, 0, -1):
            start = prev[col_idx][cursor]
            if start < 0:
                start = 0
            boundaries[col_idx - 1] = start
            cursor = start

        columns: list[list[list[str]]] = []
        for col_idx in range(col_count):
            start = boundaries[col_idx]
            end = boundaries[col_idx + 1]
            blocks = list(parcel_blocks[start:end])
            if col_idx == col_count - 1 and total_block is not None:
                blocks.append(total_block)
            columns.append(blocks)

        parts.append("<table class='ksh-flow'><tbody><tr>")
        width_pct = 100 / col_count
        for col in range(col_count):
            parts.append(f"<td class='ksh-flow-cell' style='width:{width_pct:.4f}%;'><table class='ksh-column'><tbody>")
            block_index_in_column = 0
            for block_rows in columns[col]:
                if block_index_in_column > 0:
                    parts.append("<tr class='spacer'><td colspan='5'></td></tr>")
                parts.extend(block_rows)
                block_index_in_column += 1

            if block_index_in_column == 0:
                parts.append("<tr><td colspan='5'><div class='ksh-empty'></div></td></tr>")

            parts.append("</tbody></table></td>")
        parts.append("</tr></tbody></table>")
        return "\n".join(parts)

    parts.append("<table><tbody>")
    has_section = False

    def _append_spacer_row() -> None:
        parts.append("<tr class='spacer'><td colspan='5'></td></tr>")

    for parcel in bundle.parcels:
        if has_section:
            _append_spacer_row()
        has_section = True
        parts.extend(_parcel_rows(parcel))

    if show_total_table:
        if has_section:
            _append_spacer_row()
        parts.extend(_total_rows())

    parts.append("</tbody></table>")
    return "\n".join(parts)
