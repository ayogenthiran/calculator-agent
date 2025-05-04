import yaml
import os

from src.llm.chatgpt import ChatGPTClient
from src.agents.stepwise_agent import StepwiseCalculatorAgent


# ------------- Load configs -------------

config_file = 'config/stepwise_agent_config.yaml'

assert os.path.exists(config_file), f"Config file not found at {config_file}"

config = yaml.safe_load(open(config_file))


# ------------- Create LLM client -------------

config['tool_call_required'] = 'required'
config['api_key'] = os.environ.get(config['openai_key_env_var'])
llm_client = ChatGPTClient(config)


# ------------- Run tests -------------

agent = StepwiseCalculatorAgent(llm_client, config)

# ans = agent.run('10 + 5 * 3')

ans = agent.run('10 + 5 * 3 - 8 / 2')

# ans = agent.run('10 + 5 * 3 - 8 / 2 * 3 + 1')

# ans = agent.run('10.3 + 5.44 * 3.1 - 8.776 / 2.2 * 3.44 + 1.23')

print(ans)
