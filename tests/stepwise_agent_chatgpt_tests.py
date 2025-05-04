import pytest
import os
import yaml

from src.agents.stepwise_agent import StepwiseCalculatorAgent
from src.llm.chatgpt import ChatGPTClient


def create_agent(config_overrides=None):
    # ------------- Load configs -------------
    config_file = 'config/stepwise_agent_config.yaml'
    assert os.path.exists(config_file), f"Config file not found at {config_file}"
    config = yaml.safe_load(open(config_file))

    # ------------- Create LLM client -------------
    config['tool_call_required'] = 'required'
    config['api_key'] = os.environ.get(config['openai_key_env_var'])
    llm_client = ChatGPTClient(config)

    config['tool_call_required'] = 'required'
    config['max_calls'] = 5

    if config_overrides:
        config.update(config_overrides)

    return StepwiseCalculatorAgent(llm_client, config)


@pytest.fixture
def agent():
    return create_agent()


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


# @pytest.mark.parametrize("expression, expected_result", test_expressions_1)
# def test_expressions(agent, expression, expected_result):
#     result = agent.run(expression)
#     assert pytest.approx(result, rel=1e-6) == expected_result


test_expressions_2 = test_expressions_1

@pytest.mark.parametrize("expression, expected_result", test_expressions_2)
def test_prompts_with_tool_call_returned(agent, expression, expected_result):
    agent = create_agent(config_overrides={'return_tool_call_msgs': True, 'append_messages': False})
    result = agent.run(expression)
    assert pytest.approx(result, rel=1e-6) == expected_result


test_expressions_3 = test_expressions_1

@pytest.mark.parametrize("expression, expected_result", test_expressions_3)
def test_prompts_with_previous_messages_appended(agent, expression, expected_result):
    agent = create_agent(config_overrides={'return_tool_call_msgs': True, 'append_messages': True})
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





