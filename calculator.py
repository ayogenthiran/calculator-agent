#!/usr/bin/env python3
"""
Calculator Agent - Main entry point
This script provides a simple way to run the calculator agent from the command line.
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the necessary modules
from src.orchestrator import CalculatorOrchestrator


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Calculator agent using LLM to evaluate mathematical expressions.")
    
    parser.add_argument(
        "expression", 
        nargs="?",
        help="Mathematical expression to evaluate."
    )
    
    parser.add_argument(
        "--agent", 
        "-a", 
        choices=["stepwise", "reducing"], 
        default="stepwise",
        help="Agent type to use (default: stepwise)."
    )
    
    parser.add_argument(
        "--config", 
        "-c", 
        help="Path to configuration file."
    )
    
    parser.add_argument(
        "--interactive", 
        "-i", 
        action="store_true",
        help="Run in interactive mode."
    )
    
    parser.add_argument(
        "--api-key",
        "-k",
        help="OpenAI API key. If not provided, will use the OPENAI_API_KEY environment variable."
    )
    
    return parser


def get_api_key_from_env() -> str:
    """Try to get API key from environment variables or .env file."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Try standard environment variables
    for var_name in ['OPENAI_API_KEY', 'OPEN_AI_TOKEN_2', 'OPENAI_KEY', 'OPEN_AI_KEY']:
        if var_name in os.environ and os.environ.get(var_name):
            return os.environ.get(var_name)
    
    return None


def interactive_mode(orchestrator: CalculatorOrchestrator) -> None:
    """Run the calculator in interactive mode."""
    print("Calculator Agent Interactive Mode")
    print("Enter 'exit' or 'quit' to exit")
    print("Enter 'agent [stepwise|reducing]' to change agent type")
    
    while True:
        try:
            user_input = input("\nExpression > ")
            
            if user_input.lower() in ["exit", "quit"]:
                break
                
            # Check for command to change agent
            if user_input.lower().startswith("agent "):
                parts = user_input.split()
                if len(parts) == 2:
                    try:
                        orchestrator.change_agent(parts[1])
                        print(f"Switched to {parts[1]} agent")
                    except ValueError as e:
                        print(f"Error: {e}")
                continue
            
            # Calculate expression
            try:
                result = orchestrator.calculate(user_input)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break


def main() -> None:
    """Main entry point for the calculator application."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Get API key from command line args or environment
    api_key = args.api_key or get_api_key_from_env()
    if not api_key:
        print("ERROR: No API key found.")
        print("Please set OPENAI_API_KEY in your .env file or use the --api-key option.")
        sys.exit(1)
    
    # Create orchestrator
    try:
        orchestrator = CalculatorOrchestrator(
            config_path=args.config,
            agent_type=args.agent,
            api_key=api_key
        )
    except Exception as e:
        print(f"Error initializing calculator: {e}")
        sys.exit(1)
    
    # Run in interactive mode or calculate single expression
    if args.interactive:
        interactive_mode(orchestrator)
    elif args.expression:
        try:
            result = orchestrator.calculate(args.expression)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 