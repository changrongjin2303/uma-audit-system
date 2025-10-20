from decimal import Decimal

from app.utils.unit_conversion import (
    normalize_unit,
    can_convert_units,
    get_conversion_factor,
    convert_quantity,
    convert_unit_price,
)


def test_normalize_unit_aliases():
    assert normalize_unit('平方米') == 'm²'
    assert normalize_unit('m^3') == 'm³'
    assert normalize_unit('公斤') == 'kg'
    assert normalize_unit('') == ''


def test_can_convert_units_same_family():
    assert can_convert_units('kg', 't')
    assert can_convert_units('mm', 'km')
    assert not can_convert_units('kg', 'm')


def test_get_conversion_factor():
    factor = get_conversion_factor('t', 'kg')
    assert factor == Decimal('1000')
    assert get_conversion_factor('kg', 'm') is None


def test_convert_quantity():
    result = convert_quantity(Decimal('2'), 'km', 'm')
    assert result == Decimal('2000')
    assert convert_quantity(Decimal('1'), 'kg', 'm') is None


def test_convert_unit_price():
    price = convert_unit_price(Decimal('1200'), 't', 'kg')
    assert price == Decimal('1.2')
    assert convert_unit_price(Decimal('10'), 'kg', 'm') is None
