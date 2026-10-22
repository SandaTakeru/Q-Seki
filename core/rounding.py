from __future__ import annotations

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
from typing import Optional


def decimalize(value: object) -> Decimal:
    """文字列または数値を Decimal に変換する。"""
    return Decimal(str(value))


def round_decimal(value: Decimal | int | float | str, digits: int = 0, mode: str = "half_up") -> Decimal:
    """指定桁で丸める。mode は half_up / floor / none のいずれか。"""
    decimal_value = decimalize(value)
    if mode == "none":
        return decimal_value
    if digits is None:
        return decimal_value

    quant = Decimal("1").scaleb(-digits)
    if mode == "half_up":
        return decimal_value.quantize(quant, rounding=ROUND_HALF_UP)
    if mode == "floor":
        return decimal_value.quantize(quant, rounding=ROUND_DOWN)
    raise ValueError(f"Unsupported rounding mode: {mode!r}")


def round_coordinate(value: Decimal | int | float | str, digits: int = 3, full_precision: bool = False) -> Decimal:
    """座標値を指定桁で丸める。full_precision=True なら丸めない。"""
    decimal_value = decimalize(value)
    if full_precision:
        return decimal_value
    return round_decimal(decimal_value, digits=digits, mode="half_up")


def rounded_display(value: Decimal | int | float | str, digits: int = 3, full_precision: bool = False) -> str:
    """HTML表示用の固定桁文字列を返す。"""
    decimal_value = round_coordinate(value, digits=digits, full_precision=full_precision)
    return format(decimal_value, f".{digits}f")


def area_round(value: Decimal, digits: int = 2, mode: str = "floor") -> Decimal:
    """面積の端数処理を実施する。"""
    if mode == "none":
        return value
    return round_decimal(value, digits=digits, mode=mode)
