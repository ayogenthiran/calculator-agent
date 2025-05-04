#!/usr/bin/env python3
import sys
import os
import argparse
from dotenv import load_dotenv

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import CalculatorOrchestrator


# Read the API key directly from .env file or environment
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
        help="OpenAI API key. If not provided, will try to load from environment or .env file."
    )
    
    return parser


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
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: No API key found. Please provide an API key using --api-key or set the OPENAI_API_KEY environment variable.")
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