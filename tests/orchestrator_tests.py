#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so that src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import CalculatorOrchestrator

# Read the API key directly from .env file
def get_api_key():
    """Get the API key from the .env file or environment variables."""
    # Try to load from .env file first
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.strip().split('=', 1)[1]
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    # If not found, try environment variables
    for var_name in ['OPENAI_API_KEY', 'OPEN_AI_TOKEN_2', 'OPENAI_KEY', 'OPEN_AI_KEY']:
        if var_name in os.environ:
            return os.environ.get(var_name)
    
    return None

# Get the API key
API_KEY = get_api_key()
if not API_KEY:
    print("ERROR: No API key found. Please set OPENAI_API_KEY environment variable or add it to .env file.")
    sys.exit(1)


def test_both_agents_with_same_expression():
    """Test both agents with the same expression and compare results."""
    # Set up test expression
    expression = "10 + 5 * 3 - 8 / 2"
    expected_result = 21.0  # (10 + 15 - 4) = 21
    
    # Create orchestrator with stepwise agent
    orchestrator = CalculatorOrchestrator(agent_type="stepwise", api_key=API_KEY)
    
    # Calculate with stepwise agent
    stepwise_result = orchestrator.calculate(expression)
    print(f"Stepwise result for '{expression}': {stepwise_result}")
    
    # Verify stepwise result
    assert stepwise_result == expected_result, f"Expected {expected_result}, got {stepwise_result}"
    
    # Switch to reducing agent
    orchestrator.change_agent("reducing")
    
    # Calculate with reducing agent
    reducing_result = orchestrator.calculate(expression)
    print(f"Reducing result for '{expression}': {reducing_result}")
    
    # Verify reducing result
    assert reducing_result == expected_result, f"Expected {expected_result}, got {reducing_result}"
    
    print("Both agents produced the correct result!")


def test_agent_switching():
    """Test switching between agents."""
    orchestrator = CalculatorOrchestrator(agent_type="stepwise", api_key=API_KEY)
    assert orchestrator.agent_type == "stepwise"
    
    orchestrator.change_agent("reducing")
    assert orchestrator.agent_type == "reducing"
    
    print("Agent switching works correctly!")


def run_tests():
    """Run all tests."""
    print("Running orchestrator tests...")
    
    # Test agent switching
    test_agent_switching()
    
    # Test both agents
    test_both_agents_with_same_expression()
    
    print("All tests passed!")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run tests
    run_tests() 