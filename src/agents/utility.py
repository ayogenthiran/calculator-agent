import re
import ast
from typing import Union, Optional

Number = Union[int, float]


def validate_expression(expression: str, max_expression_length: int) -> bool:
    if len(expression) > max_expression_length:
        raise ValueError(f"Expression exceeds maximum length of {max_expression_length} characters")

    pattern = r'^[\d\s\+\-\*\/\(\)\.]+$'  # Only digits, spaces, and basic arithmetic operators are allowed

    if re.match(pattern, expression) is None:
        raise ValueError(f"Invalid characters in the expression: {expression}")

    return True


def float_to_str(f: float) -> str:
    return f'{f: g}'.strip()


def create_number_pattern(num: Union[int, float]) -> str:
    if isinstance(num, int):
        return r'\b' + str(num) + r'\b'
    else:
        # Handle both integer and decimal representations
        return r'\b' + float_to_str(num).replace('.', r'\.?') + r'\b'


def reduce_expression(expression: str, a: Number, b: Number, op: str, result: Number) -> str:
    """
    Reduce a mathematical expression by replacing a specific operation with its result.
    Handle special case of operations inside parentheses.
    
    Args:
        expression: The full expression
        a: First operand
        b: Second operand
        op: Operation ('+', '-', '*', '/')
        result: Result of the operation
        
    Returns:
        The reduced expression with the operation replaced by its result
    """
    # Convert numbers to strings as they might be used in the expression
    a_str = float_to_str(a)
    b_str = float_to_str(b)
    result_str = float_to_str(result)
    
    # Handle special case of operations in parentheses like "(10 + 5)"
    if "(" in expression and ")" in expression:
        # Try to find the exact operation in parentheses
        parentheses_pattern = r'\(' + r'\s*' + create_number_pattern(a) + r'\s*' + re.escape(op) + r'\s*' + create_number_pattern(b) + r'\s*' + r'\)'
        if re.search(parentheses_pattern, expression):
            # Replace the entire parenthetical expression
            new_expression = re.sub(parentheses_pattern, result_str, expression, count=1)
            return new_expression
    
    # Standard case: pattern = number op number (with boundaries)
    pattern = create_number_pattern(a) + r'\s*' + re.escape(op) + r'\s*' + create_number_pattern(b)
    new_expression = re.sub(pattern, result_str, expression, count=1)
    
    # If the expression didn't change, try a fallback approach with string replacement
    if new_expression == expression:
        # This is a more direct approach but less precise
        op_pattern = f"{a_str}\\s*\\{op}\\s*{b_str}"
        new_expression = re.sub(op_pattern, result_str, expression, count=1)
    
    return new_expression


def safe_eval(expression: str) -> Optional[Number]:
    """Safely evaluate a mathematical expression."""
    try:
        # Remove spaces and ensure the expression contains only allowed characters
        clean_expr = expression.strip()
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', clean_expr):
            return None
            
        # Use a safer evaluation mechanism
        return eval(clean_expr)
    except:
        return None
