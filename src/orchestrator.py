import os
import yaml
from typing import Dict, Any, Optional, Union, List

from src.llm.chatgpt import ChatGPTClient
from src.agents.stepwise_agent import StepwiseCalculatorAgent
from src.agents.reducing_agent import ReducingCalculatorAgent


class CalculatorOrchestrator:
    """
    Orchestrator for the calculator application. Manages agent selection,
    configuration loading, and provides a unified interface for calculations.
    """
    
    AGENT_TYPES = {
        "stepwise": StepwiseCalculatorAgent,
        "reducing": ReducingCalculatorAgent
    }
    
    # List of environment variable names to check for API key
    API_KEY_ENV_VARS = [
        "OPENAI_API_KEY",
        "OPEN_AI_TOKEN_2",
        "OPENAI_KEY",
        "OPEN_AI_KEY"
    ]
    
    def __init__(self, config_path: Optional[str] = None, agent_type: str = "stepwise", api_key: Optional[str] = None) -> None:
        """
        Initialize the calculator orchestrator.
        
        Args:
            config_path: Path to the configuration file. If None, will use default config for the agent type.
            agent_type: Type of agent to use ("stepwise" or "reducing").
            api_key: OpenAI API key. If provided, it will override the environment variable.
        """
        self.agent_type = agent_type.lower()
        self.api_key = api_key
        
        if self.agent_type not in self.AGENT_TYPES:
            raise ValueError(f"Invalid agent type: {agent_type}. Must be one of {list(self.AGENT_TYPES.keys())}")
        
        # Load configuration
        if config_path is None:
            config_path = f"config/{agent_type}_agent_config.yaml"
            
        self.config = self._load_config(config_path)
        
        # Create LLM client
        self.llm_client = self._create_llm_client()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _create_llm_client(self) -> ChatGPTClient:
        """Create an LLM client with the loaded configuration."""
        # Set additional required config for ChatGPTClient
        self.config['tool_call_required'] = 'required'
        
        # Use directly provided API key if available
        if self.api_key:
            self.config['api_key'] = self.api_key
            return ChatGPTClient(self.config)
        
        # Try to get API key from environment variable specified in config
        api_key = None
        env_var = self.config.get('openai_key_env_var')
        
        if env_var:
            api_key = os.environ.get(env_var)
        
        # If not found, try other common environment variable names
        if not api_key:
            for var_name in self.API_KEY_ENV_VARS:
                if var_name in os.environ:
                    api_key = os.environ.get(var_name)
                    print(f"Using API key from environment variable: {var_name}")
                    break
        
        # If still not found, try to read directly from .env file
        if not api_key:
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in self.API_KEY_ENV_VARS:
                                api_key = value
                                print(f"Using API key from .env file with key: {key}")
                                break
            except Exception as e:
                print(f"Error reading .env file: {e}")
        
        if not api_key:
            env_vars_tried = [env_var] if env_var else []
            env_vars_tried.extend(self.API_KEY_ENV_VARS)
            raise EnvironmentError(f"API key not found in any of these environment variables: {', '.join(env_vars_tried)}")
        
        self.config['api_key'] = api_key
        
        return ChatGPTClient(self.config)
    
    def _ensure_agent_config(self, agent_type: str) -> None:
        """Ensure that the configuration contains all required keys for the agent type."""
        # Get the current config keys
        config_keys = set(self.config.keys())
        
        # Define required keys for each agent type
        required_keys = {
            "stepwise": {"system_prompt", "initial_prompt", "subsequent_prompt", "max_llm_calls", "max_expression_length"},
            "reducing": {"system_prompt", "prompt", "max_llm_calls", "max_expression_length"}
        }
        
        # If this is a different agent type, load its specific config and merge
        if agent_type != self.agent_type or not required_keys[agent_type].issubset(config_keys):
            agent_config_path = f"config/{agent_type}_agent_config.yaml"
            if os.path.exists(agent_config_path):
                with open(agent_config_path, 'r') as f:
                    agent_config = yaml.safe_load(f)
                
                # Merge configs, keeping existing values like API key
                for key, value in agent_config.items():
                    if key not in self.config or key in required_keys[agent_type]:
                        self.config[key] = value
            else:
                print(f"Warning: Config file for {agent_type} agent not found at {agent_config_path}")
    
    def _create_agent(self) -> Union[StepwiseCalculatorAgent, ReducingCalculatorAgent]:
        """Create an agent of the specified type."""
        # Ensure configuration has all required keys for this agent type
        self._ensure_agent_config(self.agent_type)
        
        agent_class = self.AGENT_TYPES[self.agent_type]
        return agent_class(self.llm_client, self.config)
    
    def calculate(self, expression: str) -> Optional[float]:
        """
        Calculate the result of a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate.
            
        Returns:
            The result of the calculation, or None if calculation failed.
        """
        return self.agent.run(expression)
    
    def change_agent(self, agent_type: str, config_path: Optional[str] = None) -> None:
        """
        Change the agent type.
        
        Args:
            agent_type: The new agent type ("stepwise" or "reducing").
            config_path: Optional path to a new configuration file.
        """
        self.agent_type = agent_type.lower()
        
        if self.agent_type not in self.AGENT_TYPES:
            raise ValueError(f"Invalid agent type: {agent_type}. Must be one of {list(self.AGENT_TYPES.keys())}")
        
        if config_path:
            self.config = self._load_config(config_path)
            self.llm_client = self._create_llm_client()
        
        self.agent = self._create_agent()
    
    def load_config(self, config_path: str) -> None:
        """
        Load a new configuration file.
        
        Args:
            config_path: Path to the new configuration file.
        """
        self.config = self._load_config(config_path)
        self.llm_client = self._create_llm_client()
        self.agent = self._create_agent() 