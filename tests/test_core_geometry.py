from decimal import Decimal

from core.geometry import normalize_ring, polygon_twice_area


def test_square_area_ccw_and_cw():
    square_ccw = [
        (Decimal("0"), Decimal("0")),
        (Decimal("10"), Decimal("0")),
        (Decimal("10"), Decimal("10")),
        (Decimal("0"), Decimal("10")),
    ]
    square_cw = [
        (Decimal("0"), Decimal("0")),
        (Decimal("0"), Decimal("10")),
        (Decimal("10"), Decimal("10")),
        (Decimal("10"), Decimal("0")),
    ]
    assert polygon_twice_area(normalize_ring(square_ccw, start="north")) == Decimal("200")
    assert polygon_twice_area(normalize_ring(square_cw, start="north")) == Decimal("200")


def test_rounding_rules():
    assert Decimal("0.001") == Decimal("0.0005").quantize(Decimal("0.001"), rounding="ROUND_HALF_UP")
    assert Decimal("0.000") == Decimal("0.0004").quantize(Decimal("0.001"), rounding="ROUND_HALF_UP")


def test_full_precision_changes_result():
    ring = [
        (Decimal("0.0000"), Decimal("0.0000")),
        (Decimal("1.23456"), Decimal("0.0000")),
        (Decimal("1.23456"), Decimal("1.23456")),
        (Decimal("0.0000"), Decimal("1.23456")),
    ]
    assert polygon_twice_area(normalize_ring(ring, start="north")) != Decimal("0")


def test_hole_ring_area_is_subtracted():
    outer = [
        (Decimal("0"), Decimal("0")),
        (Decimal("10"), Decimal("0")),
        (Decimal("10"), Decimal("10")),
        (Decimal("0"), Decimal("10")),
    ]
    hole = [
        (Decimal("2"), Decimal("2")),
        (Decimal("8"), Decimal("2")),
        (Decimal("8"), Decimal("8")),
        (Decimal("2"), Decimal("8")),
    ]
    total = polygon_twice_area(outer) - polygon_twice_area(hole)
    assert total == Decimal("200") - Decimal("72")


def test_multiple_parcels_and_total():
    parcel1 = [
        (Decimal("0"), Decimal("0")),
        (Decimal("10"), Decimal("0")),
        (Decimal("10"), Decimal("10")),
        (Decimal("0"), Decimal("10")),
    ]
    parcel2 = [
        (Decimal("0"), Decimal("0")),
        (Decimal("5"), Decimal("0")),
        (Decimal("5"), Decimal("5")),
        (Decimal("0"), Decimal("5")),
    ]
    total = polygon_twice_area(normalize_ring(parcel1, start="north")) + polygon_twice_area(normalize_ring(parcel2, start="north"))
    assert total == Decimal("200") + Decimal("50")
