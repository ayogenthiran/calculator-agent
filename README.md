# Calculator Agent

A calculator application that uses LLMs (Large Language Models) to evaluate mathematical expressions step by step.

## Overview

This project demonstrates how LLMs can be used to solve multi-step mathematical expressions by breaking them down into individual calculation steps. The application supports two different calculation strategies:

1. **Stepwise Agent**: Maintains the full original expression and all previous calculation steps.
2. **Reducing Agent**: Progressively simplifies the expression by replacing calculated portions.

## Features

- Step-by-step calculation breakdown
- Support for basic mathematical operations (+, -, *, /)
- Parentheses handling for complex expressions
- Modern web interface using Streamlit
- Support for different LLM models
- Clean visualization of calculation steps

## Project Structure

```
calculator-agent/
├── config/                 # Configuration files
│   ├── reducing_agent_config.yaml
│   └── stepwise_agent_config.yaml
├── src/                    # Source code
│   ├── __init__.py         # Python package marker
│   ├── agents/             # Agent implementations
│   │   ├── reducing_agent.py
│   │   ├── stepwise_agent.py
│   │   ├── tool_call_result.py
│   │   └── utility.py
│   ├── llm/                # LLM client implementations
│   │   ├── chatgpt.py
│   │   └── llm_base.py
│   ├── tools/              # Tool implementations
│   │   └── calculator.py
│   └── orchestrator.py     # Orchestrator for agent management
├── app.py                  # Streamlit web interface
├── tests/                  # Test files
├── .env                    # Environment variables (API keys)
└── requirements.txt        # Python dependencies
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip3 install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
## Configuration

The calculator uses GPT-3.5-turbo by default. You can change the model by editing the configuration files in the `config/` directory.

To use a different OpenAI model, modify the `model` parameter in:
- `config/stepwise_agent_config.yaml` 
- `config/reducing_agent_config.yaml`

Available model options include:
- `gpt-3.5-turbo` (default, faster)
- `gpt-4o` (more powerful)
- `gpt-4o-mini` (balances speed and accuracy)

## Usage

### Web Interface

The easiest way to use the calculator is through the Streamlit web interface:

```
streamlit run app.py
```

This will start a local web server and open the calculator app in your browser. Features include:
- Interactive expression input
- Agent type selection (stepwise or reducing)
- Step-by-step calculation display
- Calculation history
- Support for complex expressions with parentheses

### Example Expressions

Try these expressions to see how the calculator works:
- `10 + 5 * 3 - 8 / 2` (basic operations with order of precedence)
- `2 * (10 + 5) - 12 / 3` (parentheses)
- `(8 - 3) * (4 + 2) / 3` (nested operations)

## How It Works

The calculator agent:

1. Takes a mathematical expression as input
2. The orchestrator initializes the appropriate agent strategy
3. The agent queries an LLM with the expression
4. The LLM identifies the next calculation step to perform
5. The agent executes the calculation and updates its state
6. Steps 3-5 repeat until the final result is reached

### Agent Types

**Stepwise Agent**:
- Best for educational purposes
- Shows all steps at once
- Maintains the original expression
- More reliable for complex expressions

**Reducing Agent**:
- Shows how expressions get simplified
- Replaces calculated parts with their results
- Demonstrates incremental problem-solving
- Shows remaining expression at each step

## License

This project is provided as an educational demo.
