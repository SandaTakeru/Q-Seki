from decimal import Decimal

from core.geometry import normalize_ring, polygon_twice_area
from core.report import ReportBundle, ParcelReport, PartReport, VertexRow, build_html_report


def test_html_contains_required_sections():
    rows = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('10'), x_mul_delta_y=Decimal('0')),
        VertexRow(name='B', x=Decimal('10'), y=Decimal('0'), delta_y=Decimal('10'), x_mul_delta_y=Decimal('100')),
        VertexRow(name='C', x=Decimal('10'), y=Decimal('10'), delta_y=Decimal('-10'), x_mul_delta_y=Decimal('-100')),
        VertexRow(name='D', x=Decimal('0'), y=Decimal('10'), delta_y=Decimal('-10'), x_mul_delta_y=Decimal('0')),
    ]
    parcel = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows, twice_area=Decimal('200'), area=Decimal('100.00'))],
        total_area=Decimal('100.00'),
        reference_area=Decimal('200'),
    )
    bundle = ReportBundle(parcels=[parcel], total_area=Decimal('100.00'), total_reference_area=Decimal('200'))
    html = build_html_report(bundle)
    assert '12-1' in html
    assert '点名' in html
    assert '倍面積' in html
    assert '合計' in html
    assert '面積の合計' in html
    assert '地積の合計' in html
    assert html.count('<table>') == 1


def test_html_total_table_can_be_hidden():
    rows = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('10'), x_mul_delta_y=Decimal('0')),
        VertexRow(name='B', x=Decimal('10'), y=Decimal('0'), delta_y=Decimal('10'), x_mul_delta_y=Decimal('100')),
        VertexRow(name='C', x=Decimal('10'), y=Decimal('10'), delta_y=Decimal('-10'), x_mul_delta_y=Decimal('-100')),
        VertexRow(name='D', x=Decimal('0'), y=Decimal('10'), delta_y=Decimal('-10'), x_mul_delta_y=Decimal('0')),
    ]
    parcel = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows, twice_area=Decimal('200'), area=Decimal('100.00'))],
        total_area=Decimal('100.00'),
        reference_area=Decimal('200'),
    )
    bundle = ReportBundle(parcels=[parcel], total_area=Decimal('100.00'), total_reference_area=Decimal('200'))
    html = build_html_report(bundle, show_total_table=False)
    assert '面積の合計' not in html
    assert '地積の合計' not in html


def test_hole_total_twice_area_is_sum_of_part_twice_areas():
    outer_rows = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('100')),
        VertexRow(name='B', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('50')),
    ]
    hole_rows = [
        VertexRow(name='E', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('-40')),
        VertexRow(name='F', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('-10')),
    ]

    # twice_area フィールドは意図的に不整合値を入れて、表示が rows 合計基準であることを確認
    parcel = ParcelReport(
        label='12-1',
        parts=[
            PartReport(title='外郭', rows=outer_rows, twice_area=Decimal('999'), area=Decimal('100.00')),
            PartReport(title='穴1', rows=hole_rows, twice_area=Decimal('999'), area=Decimal('-18.00'), is_hole=True),
        ],
        total_area=Decimal('82.00'),
        reference_area=Decimal('0'),
    )
    bundle = ReportBundle(parcels=[parcel], total_area=Decimal('82.00'), total_reference_area=Decimal('0'))

    html = build_html_report(bundle)
    # outer=150, hole=-50, 外郭-穴=100, 面積=50, 地積=50.00
    assert '外郭-穴）' in html
    assert '100.000000' in html
    assert '50.0000000' in html
    assert '50.00 ㎡' in html
    assert html.count("<th class='colhead'>点名</th>") == 2


def test_html_uses_spacer_rows_between_sections_and_total():
    rows1 = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
        VertexRow(name='B', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
    ]
    rows2 = [
        VertexRow(name='C', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('20')),
        VertexRow(name='D', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('20')),
    ]

    parcel1 = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows1, twice_area=Decimal('20'), area=Decimal('10.00'))],
        total_area=Decimal('10.00'),
        reference_area=Decimal('20'),
    )
    parcel2 = ParcelReport(
        label='12-2',
        parts=[PartReport(title='外郭', rows=rows2, twice_area=Decimal('40'), area=Decimal('20.00'))],
        total_area=Decimal('20.00'),
        reference_area=Decimal('40'),
    )

    bundle = ReportBundle(
        parcels=[parcel1, parcel2],
        total_area=Decimal('30.00'),
        total_reference_area=Decimal('60'),
    )

    html = build_html_report(bundle, show_total_table=True)

    assert html.count('<table>') == 1
    assert "tr.spacer td{border:none" in html
    assert html.count("<tr class='spacer'><td colspan='5'></td></tr>") == 2
    assert html.count("<th class='colhead'>点名</th>") == 2


def test_html_flow_columns_splits_into_cards():
    rows1 = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
        VertexRow(name='B', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
    ]
    rows2 = [
        VertexRow(name='C', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('20')),
        VertexRow(name='D', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('20')),
    ]

    parcel1 = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows1, twice_area=Decimal('20'), area=Decimal('10.00'))],
        total_area=Decimal('10.00'),
        reference_area=Decimal('20'),
    )
    parcel2 = ParcelReport(
        label='12-2',
        parts=[PartReport(title='外郭', rows=rows2, twice_area=Decimal('40'), area=Decimal('20.00'))],
        total_area=Decimal('20.00'),
        reference_area=Decimal('40'),
    )

    bundle = ReportBundle(
        parcels=[parcel1, parcel2],
        total_area=Decimal('30.00'),
        total_reference_area=Decimal('60'),
    )

    html = build_html_report(bundle, column_count=3, show_total_table=True)

    assert "<table class='ksh-flow'><tbody><tr>" in html
    assert "table-layout:fixed" in html
    assert ".ksh-flow > tbody > tr > td.ksh-flow-cell" in html
    assert "<table class='ksh-column'><tbody>" in html
    assert html.count("class='ksh-flow-cell'") == 2
    assert html.count('<table') == 3
    assert html.count("<tr class='spacer'><td colspan='5'></td></tr>") >= 1

    total_pos = html.rfind("<th colspan='5' class='section'>合計</th>")
    last_cell_pos = html.rfind("class='ksh-flow-cell'")
    assert total_pos > 0
    assert total_pos > last_cell_pos


def test_html_flow_columns_places_cards_in_column_major_order():
    base_rows = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
        VertexRow(name='B', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('10')),
    ]
    parcels = [
        ParcelReport(
            label=f'P{i}',
            parts=[PartReport(title='外郭', rows=base_rows, twice_area=Decimal('20'), area=Decimal('10.00'))],
            total_area=Decimal('10.00'),
            reference_area=Decimal('20'),
        )
        for i in range(1, 10)
    ]

    bundle = ReportBundle(
        parcels=parcels,
        total_area=Decimal('90.00'),
        total_reference_area=Decimal('180'),
    )

    html = build_html_report(bundle, column_count=3, show_total_table=False)
    col_start = "<table class='ksh-column'><tbody>"
    columns: list[str] = []
    start = 0
    for _ in range(3):
        pos = html.find(col_start, start)
        assert pos >= 0
        body_start = pos + len(col_start)
        body_end = html.find("</tbody></table></td>", body_start)
        assert body_end >= 0
        columns.append(html[body_start:body_end])
        start = body_end

    assert "P1" in columns[0] and "P2" in columns[0] and "P3" in columns[0]
    assert "P4" in columns[1] and "P5" in columns[1] and "P6" in columns[1]
    assert "P7" in columns[2] and "P8" in columns[2] and "P9" in columns[2]


def test_normalized_vertices_are_counterclockwise():
    square = [
        (Decimal('0'), Decimal('0')),
        (Decimal('0'), Decimal('10')),
        (Decimal('10'), Decimal('10')),
        (Decimal('10'), Decimal('0')),
    ]
    normalized = normalize_ring(square, start='north')
    assert normalized[0][1] == Decimal('10')
    assert polygon_twice_area(normalized) == Decimal('200')


def test_full_precision_display_preserves_trailing_zeros():
    rows = [
        VertexRow(name='A', x=Decimal('10.1200'), y=Decimal('20.5000'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('5.4000')),
        VertexRow(name='B', x=Decimal('10.1200'), y=Decimal('20.5000'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('5.4000')),
    ]

    parcel = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows, twice_area=Decimal('10.8000'), area=Decimal('5.40'))],
        total_area=Decimal('5.40'),
        reference_area=Decimal('10.8000'),
    )
    bundle = ReportBundle(parcels=[parcel], total_area=Decimal('5.40'), total_reference_area=Decimal('10.8000'))

    html = build_html_report(bundle, full_precision=True)

    assert '10.1200' in html
    assert '20.5000' in html
    assert '5.4000' in html
    assert '10.8000' in html


def test_tsubo_rows_are_rendered_from_truncated_area():
    rows = [
        VertexRow(name='A', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('100.12')),
        VertexRow(name='B', x=Decimal('0'), y=Decimal('0'), delta_y=Decimal('0'), x_mul_delta_y=Decimal('100.12')),
    ]
    parcel = ParcelReport(
        label='12-1',
        parts=[PartReport(title='外郭', rows=rows, twice_area=Decimal('200.24'), area=Decimal('100.129'))],
        total_area=Decimal('100.129'),
        reference_area=Decimal('200.24'),
    )
    bundle = ReportBundle(parcels=[parcel], total_area=Decimal('100.129'), total_reference_area=Decimal('200.24'))

    html = build_html_report(bundle, area_digits=2, show_total_table=True, show_tsubo=True)

    # 地積は切り捨てで 100.12、坪換算は 100.12 * 121 / 400 = 30.2863 -> 切り捨てで 30.28
    assert '地積（坪）' in html
    assert '地積の合計（坪）' in html
    assert '30.28 坪' in html
