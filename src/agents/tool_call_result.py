from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ToolCallResult:
    results: List[Tuple[float, str]]    # [(result, tool_call_id)]
    is_final_step: bool
    call_steps: List[str]
    remaining_expression: str
