#!/usr/bin/env python3
"""
Direct test script that uses API key from .env file.
"""

import os
import sys
from dotenv import load_dotenv

# Add project directory to Python path
sys.path.insert(0, os.path.abspath('.'))

from src.orchestrator import CalculatorOrchestrator

def get_api_key():
    """Get the API key from environment variables."""
    # Load environment variables from .env file
    load_dotenv()
    
    for var_name in ["OPENAI_API_KEY", "OPEN_AI_TOKEN_2", "OPENAI_KEY", "OPEN_AI_KEY"]:
        if var_name in os.environ:
            return os.environ.get(var_name)
    
    print("ERROR: No API key found in environment variables.")
    print("Please set OPENAI_API_KEY in your .env file.")
    sys.exit(1)

def test_calculator():
    """Test the calculator with a simple expression."""
    # Get API key from environment
    api_key = get_api_key()
    
    print("Creating orchestrator with API key from environment...")
    
    # Create orchestrator with API key
    orchestrator = CalculatorOrchestrator(api_key=api_key)
    
    # Test expression
    expression = "10 + 5 * 3 - 8 / 2"
    print(f"Calculating: {expression}")
    
    # Calculate
    result = orchestrator.calculate(expression)
    print(f"Result: {result}")
    
    # Switch agent
    print("Switching to reducing agent...")
    orchestrator.change_agent("reducing")
    
    # Calculate again
    print(f"Calculating with reducing agent: {expression}")
    result = orchestrator.calculate(expression)
    print(f"Result: {result}")
    
    print("Test completed successfully!")


if __name__ == "__main__":
    test_calculator() 