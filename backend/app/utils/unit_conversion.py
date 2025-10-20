"""单位换算工具。

提供单位标准化、量值换算与单价换算能力，用于在分析环节对齐项目材料与市场信息价材料的计量单位。
"""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

# 基础单位组定义，值表示 1 个该单位折算到基准单位（长度:m、面积:m²、体积:m³、重量:kg）
_UNIT_FACTORS: Dict[str, Dict[str, Decimal]] = {
    "length": {
        "mm": Decimal("0.001"),
        "cm": Decimal("0.01"),
        "m": Decimal("1"),
        "km": Decimal("1000"),
    },
    "area": {
        "mm²": Decimal("0.000001"),
        "cm²": Decimal("0.0001"),
        "m²": Decimal("1"),
        "km²": Decimal("1000000"),
    },
    "volume": {
        "cm³": Decimal("0.000001"),
        "dm³": Decimal("0.001"),
        "L": Decimal("0.001"),
        "mm³": Decimal("0.000000001"),
        "m³": Decimal("1"),
    },
    "weight": {
        "mg": Decimal("0.000001"),
        "g": Decimal("0.001"),
        "kg": Decimal("1"),
        "t": Decimal("1000"),
    },
}

# 单位别名映射，统一常见中文、大小写、符号写法
_UNIT_ALIASES: Dict[str, str] = {
    "㎡": "m²",
    "m2": "m²",
    "m^2": "m²",
    "平方": "m²",
    "平方米": "m²",
    "平米": "m²",
    "cm2": "cm²",
    "cm^2": "cm²",
    "平方厘米": "cm²",
    "mm2": "mm²",
    "mm^2": "mm²",
    "平方毫米": "mm²",
    "㎜²": "mm²",
    "立方": "m³",
    "立方米": "m³",
    "立米": "m³",
    "m3": "m³",
    "m^3": "m³",
    "立方厘米": "cm³",
    "cm3": "cm³",
    "cm^3": "cm³",
    "立方分米": "dm³",
    "dm3": "dm³",
    "dm^3": "dm³",
    "mm3": "mm³",
    "mm^3": "mm³",
    "立方毫米": "mm³",
    "升": "L",
    "公升": "L",
    "l": "L",
    "L": "L",
    "ml": "cm³",
    "mL": "cm³",
    "毫升": "cm³",
    "米": "m",
    "M": "m",
    "cm": "cm",
    "厘米": "cm",
    "mm": "mm",
    "毫米": "mm",
    "km": "km",
    "公里": "km",
    "千米": "km",
    "平方公里": "km²",
    "平方千米": "km²",
    "克": "g",
    "千克": "kg",
    "公斤": "kg",
    "Kg": "kg",
    "KG": "kg",
    "吨": "t",
    "T": "t",
    "mg": "mg",
}


def normalize_unit(unit: str) -> str:
    """标准化单位表示，未知单位返回小写去空格形式。"""
    if not unit:
        return ""
    cleaned = unit.strip()
    if not cleaned:
        return ""
    # 先走别名映射
    alias = _UNIT_ALIASES.get(cleaned)
    if alias:
        return alias
    alias = _UNIT_ALIASES.get(cleaned.lower())
    if alias:
        return alias
    return cleaned.lower()


def _find_unit_family(unit: str) -> Optional[str]:
    for family, factors in _UNIT_FACTORS.items():
        if unit in factors:
            return family
    return None


def can_convert_units(unit1: str, unit2: str) -> bool:
    """判断两个单位是否可互相换算。"""
    if not unit1 or not unit2:
        return False
    family1 = _find_unit_family(unit1)
    family2 = _find_unit_family(unit2)
    return bool(family1 and family1 == family2)


def get_conversion_factor(from_unit: str, to_unit: str) -> Optional[Decimal]:
    """计算 1 个 from_unit 等于多少个 to_unit。无法换算返回 None。"""
    if not can_convert_units(from_unit, to_unit):
        return None
    family = _find_unit_family(from_unit)
    assert family is not None
    factors = _UNIT_FACTORS[family]
    # from/to 均在 factors 中
    factor_from = factors[from_unit]
    factor_to = factors[to_unit]
    return factor_from / factor_to


def convert_quantity(value: Decimal, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """数量换算，返回转换后的值。"""
    factor = get_conversion_factor(from_unit, to_unit)
    if factor is None:
        return None
    return value * factor


def convert_unit_price(price: Decimal, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """单价换算，将“每 from_unit 的价格”换算为“每 to_unit 的价格”。"""
    factor = get_conversion_factor(from_unit, to_unit)
    if factor is None:
        return None
    if factor == 0:
        return None
    return price / factor


def convert_price_to_target_unit(price: Decimal, original_unit: str, target_unit: str) -> Optional[Decimal]:
    """
    将原始单价从 original_unit 换算到 target_unit。
    与 convert_unit_price 等价，提供更语义化的名称以便调用。
    """
    return convert_unit_price(price, original_unit, target_unit)


__all__ = [
    "normalize_unit",
    "can_convert_units",
    "get_conversion_factor",
    "convert_quantity",
    "convert_unit_price",
    "convert_price_to_target_unit",
]
