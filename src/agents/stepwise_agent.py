import json
from typing import List, Tuple, Any, Optional

from src.agents.tool_call_result import ToolCallResult
from src.agents.utility import validate_expression

from src.tools.calculator import calculate
from src.llm.llm_base import LLMClientBase
from src.llm.chatgpt import MessageHistory


class StepwiseCalculatorAgent:
    """
   Implements a calculator agent by iteratively calling an LLM client with a prompt that contains.
   1) the full original expression
   2) the steps of the calculation so far
   At each call, the LLM will output the function arguments for calculate(a, b, op) to perform the next step
   When the LLM determines that the final step has been reached, the agent will return the final result.
   """
    def __init__(self, llm_client: LLMClientBase, config: dict) -> None:
        self.llm_client = llm_client

        self.max_expression_length: int = config['max_expression_length']

        self.system_prompt: str = config['system_prompt']
        self.subsequent_prompt: str = config['subsequent_prompt']
        self.initial_prompt: str = config['initial_prompt']

        self.max_llm_calls: int = config['max_llm_calls']
        self.return_tool_call_msgs: bool = config['return_tool_call_msgs']
        self.append_messages: bool = config['append_messages']

    def run(self, expression: str) -> Optional[float]:
        """
        Run the stepwise calculation process for the given expression.

        :param expression: The mathematical expression to evaluate
        :return: The final result of the calculation, or None if not successful
        """
        print(f"Input expression: {expression}")
        print("--- CALCULATION STEPS BEGIN ---")

        # Invalid expressions will raise an exception
        validate_expression(expression, self.max_expression_length)

        initial_prompt = self.initial_prompt.replace('{EXPRESSION}', expression)

        prompt_msg = MessageHistory()
        prompt_msg.add_system_message(self.system_prompt)
        prompt_msg.add_user_message(initial_prompt)

        steps: List[str] = []
        final_result: Optional[float] = None
        i = 1

        while True:
            # print(f'\n ================ iteration {i} ================ \n')

            # print('\n----- prompt_msg -----\n')
            # print(prompt_msg)

            response = self.llm_client.run_prompt(prompt_msg)

            result = self._process_tool_calls(response.tool_calls)

            print(f"Step {i}: {'    ,   '.join(result.call_steps)}")

            if result.is_final_step:
                final_result = result.results[-1][0]   # Last result --> first element in the tuple
                print(f"Final result: {final_result}")
                break

            steps.extend(result.call_steps)

            prompt_msg = self._prepare_next_prompt(prompt_msg, expression, steps, result.results, response)

            if i >= self.max_llm_calls:
                raise RuntimeError(f'Max LLM calls reached before final result. Max calls: {self.max_llm_calls}')

            i += 1

        print("--- CALCULATION STEPS END ---")
        return final_result

    def _process_tool_calls(self, tool_calls: List[Any]) -> ToolCallResult:
        """
        Process the tool calls returned by the LLM and perform the calculations.

        :param tool_calls: A list of tool calls from the LLM response
        :return: A ToolCallResult object containing the results and step information
        """
        if not tool_calls:
            raise RuntimeError("Error: Expected a tool call but received none.")

        results: List[Tuple[float, str]] = []
        is_final_step = False
        call_steps: List[str] = []

        # Handle the potential case of multiple tool calls returned by the LLM
        for tool_call in tool_calls:
            function_call = tool_call.function

            try:
                print(f"Processing tool call: {function_call.name}, arguments: {function_call.arguments}")
                func_args = json.loads(function_call.arguments)
                
                # Check for typo in 'op' key name ('op:' instead of 'op')
                if 'op:' in func_args and 'op' not in func_args:
                    print("Found 'op:' instead of 'op' in arguments, fixing...")
                    func_args['op'] = func_args['op:']
                    
                a = func_args['a']
                b = func_args['b']
                op = func_args['op']
                is_final_step = func_args['is_final_step']
                
                print(f"Parsed arguments - a: {a}, b: {b}, op: '{op}' (type: {type(op)}), is_final_step: {is_final_step}")
                
                # Ensure op is a valid operation string
                if not isinstance(op, str):
                    raise ValueError(f"Operation must be a string, got {type(op).__name__}: {op}")
                
                # Ensure op is one of the allowed operations
                if op not in ['+', '-', '*', '/']:
                    raise ValueError(f"Invalid operation: '{op}'. Must be one of: +, -, *, /")
                
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"Error parsing arguments: {e}")
                print(f"Raw arguments: {function_call.arguments}")
                
                # Try to fix common issues with tool call arguments
                try:
                    # Re-parse as JSON but with some preprocessing
                    fixed_args = function_call.arguments.replace("op:", "op")
                    func_args = json.loads(fixed_args)
                    
                    print(f"Attempting with fixed arguments: {fixed_args}")
                    
                    a = func_args['a']
                    b = func_args['b']
                    op = func_args['op']
                    is_final_step = func_args['is_final_step']
                    
                    print(f"Fixed and parsed: a: {a}, b: {b}, op: '{op}', is_final_step: {is_final_step}")
                except Exception as fix_error:
                    # If the fix also fails, raise the original error
                    raise RuntimeError(f"Invalid tool call arguments format: {function_call.arguments}. \n error: {e}")
                    
            result = calculate(a, b, op)

            step = f"{a} {op} {b} = {result}"
            call_steps.append(step)

            results.append((result, tool_call.id))

        return ToolCallResult(results, is_final_step, call_steps, '')

    def _prepare_next_prompt(self, prompt_msg: MessageHistory, expression: str, steps: List[str],
                             results: List[Tuple[float, str]], response: Any) -> MessageHistory:
        """
        Prepare the prompt for the next iteration of the calculation process. Several variants are possible.
        """
        steps_so_far = '\n'.join(steps)
        next_prompt = self.subsequent_prompt.replace('{EXPRESSION}', expression)
        next_prompt = next_prompt.replace('{STEPS_SO_FAR}', steps_so_far)

        # print(next_prompt)

        # Append messages to the current history
        if self.append_messages:
            if self.return_tool_call_msgs:
                prompt_msg.add_generic_message(response)

                for (result, tool_call_id) in results:
                    prompt_msg.add_tool_result_message(result, tool_call_id)

            prompt_msg.add_user_message(next_prompt)

        # Fresh message history for the next iteration
        else:
            prompt_msg = MessageHistory()
            prompt_msg.add_system_message(self.system_prompt)
            prompt_msg.add_user_message(next_prompt)

        return prompt_msg


