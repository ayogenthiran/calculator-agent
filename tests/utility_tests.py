import pytest

from src.agents.utility import validate_expression


@pytest.mark.parametrize("expression, error_type, error_message", [
    ("a + b", ValueError, "Invalid characters in the expression"),
    ("2 + 3 = 5", ValueError, "Invalid characters in the expression"),
    ("sin(30)", ValueError, "Invalid characters in the expression"),
    ("2 ^ 3", ValueError, "Invalid characters in the expression"),
    ("√16", ValueError, "Invalid characters in the expression"),
    ("2 + 3i", ValueError, "Invalid characters in the expression"),
    ("0xFF + 10", ValueError, "Invalid characters in the expression"),
    ("3.14e2 + 1", ValueError, "Invalid characters in the expression"),
])
def test_expression_with_invalid_chars(expression, error_type, error_message):
    with pytest.raises(error_type) as excinfo:
        validate_expression(expression, max_expression_length=100)
    assert error_message in str(excinfo.value)


def test_too_long_expression():
    expression = '25 + 23.87 * 30'

    with pytest.raises(ValueError) as excinfo:
        validate_expression(expression, max_expression_length=10)

    assert 'Expression exceeds maximum length' in str(excinfo.value)
