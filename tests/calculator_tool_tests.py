import pytest
from src.tools.calculator import calculate


def test_addition():
    """Test the addition operation"""
    assert calculate(1, 2, '+') == 3
    assert calculate(-1, -2, '+') == -3
    assert calculate(1.5, 2.5, '+') == 4.0


def test_subtraction():
    """Test the subtraction operation"""
    assert calculate(5, 3, '-') == 2
    assert calculate(-5, -3, '-') == -2
    assert calculate(5.5, 3.2, '-') == 2.3


def test_multiplication():
    """Test the multiplication operation"""
    assert calculate(2, 3, '*') == 6
    assert calculate(-2, 3, '*') == -6
    assert calculate(1.5, 2.0, '*') == 3.0


def test_division():
    """Test the division operation"""
    assert calculate(6, 3, '/') == 2
    assert calculate(-6, 3, '/') == -2
    assert calculate(7.5, 2.5, '/') == 3.0


def test_zero_division():
    """Test division by zero raises ZeroDivisionError"""
    with pytest.raises(ZeroDivisionError):
        calculate(5, 0, '/')


def test_invalid_operator():
    """Test invalid operator raises ValueError"""
    with pytest.raises(ValueError):
        calculate(5, 3, '^')


def test_invalid_input_type():
    """Test that invalid input types raise appropriate errors"""
    with pytest.raises(TypeError):
        calculate("5", 3, '+')  # Invalid type for a
    with pytest.raises(TypeError):
        calculate(5, "3", '+')  # Invalid type for b


def test_large_numbers():
    """Test the operation with large numbers"""
    assert calculate(1_000_000_000, 2_000_000_000, '+') == 3_000_000_000
    assert calculate(1_000_000_000, 2_000_000_000, '-') == -1_000_000_000
    assert calculate(1_000_000_000, 2, '*') == 2_000_000_000
    assert calculate(1_000_000_000, 2, '/') == 500_000_000
