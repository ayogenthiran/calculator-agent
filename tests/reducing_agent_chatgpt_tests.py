import pytest
import os
import yaml

from src.agents.reducing_agent import ReducingCalculatorAgent
from src.llm.chatgpt import ChatGPTClient


@pytest.fixture
def agent():
    # ------------- Load configs -------------
    config_file = 'config/reducing_agent_config.yaml'
    assert os.path.exists(config_file), f"Config file not found at {config_file}"
    config = yaml.safe_load(open(config_file))

    # ------------- Create LLM client -------------
    config['tool_call_required'] = 'required'
    config['api_key'] = os.environ.get(config['openai_key_env_var'])
    llm_client = ChatGPTClient(config)

    config['tool_call_required'] = 'required'
    config['max_calls'] = 5

    return ReducingCalculatorAgent(llm_client, config)


# ------------- Test valid expressions -------------

test_expressions_1 = [
    ("2 + 3", 5),
    ("2 * 3 + 4", 10),
    ("2.67 * 3.82 + 4.77", 14.9694),
    ("(3 + 2) * 4", 20),
    ("1000000 + 2000000", 3000000),
    ("0.0001 + 0.0002", 0.0003),
    ("-5 * 3", -15),
    ("7 / 2", 3.5),
    ("2 * 3 + 4 / 2 - 1", 7),
    ("(10 + 5) * 3 - 20 / 4", 40),
]


@pytest.mark.parametrize("expression, expected_result", test_expressions_1)
def test_expressions(agent, expression, expected_result):
    result = agent.run(expression)
    assert pytest.approx(result, rel=1e-6) == expected_result


# ------------- Test behavioural/ runtime scenarios -------------

# def test_max_calls_reached(agent):
#     expression = "1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 + 11 + 12 + 13 + 14 + 15"  # Lots of operations
#
#     with pytest.raises(RuntimeError) as excinfo:
#         agent.run(expression)
#
#     assert str(excinfo.value).startswith("Max LLM calls reached before final result.")
#
#     print('test_max_calls_reached passed')





