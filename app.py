#!/usr/bin/env python3
"""
Calculator Agent - Streamlit UI
A web interface for the calculator agent using Streamlit.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv
import io
import contextlib
import re

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the orchestrator
from src.orchestrator import CalculatorOrchestrator

# Page config
st.set_page_config(
    page_title="Calculator Agent",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.2rem;
    }
    .calculation-box {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .step {
        margin-bottom: 0.8rem;
        padding: 0.8rem;
        border-left: 3px solid #4e8df5;
        background-color: #f8f9fa;
        border-radius: 4px;
    }
    .final-result {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0068c9;
        padding: 1rem;
        background-color: #f0f7ff;
        border-radius: 0.5rem;
        text-align: center;
        margin-top: 1rem;
    }
    .debug-output {
        font-family: monospace;
        white-space: pre-wrap;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        font-size: 12px;
    }
    .prev-calc-summary {
        display: flex;
        flex-direction: column;
        gap: 10px;
        background-color: #f0f2f6;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    """Get the API key from environment or session state."""
    # Check if the API key is in the session state
    if "api_key" in st.session_state and st.session_state.api_key:
        return st.session_state.api_key
    
    # Check environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        st.session_state.api_key = api_key
        return api_key
    
    # If not found, return None
    return None

def create_orchestrator(agent_type="stepwise", api_key=None):
    """Create an orchestrator instance."""
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            st.error("No API key found. Please enter your OpenAI API key.")
            return None
    
    try:
        return CalculatorOrchestrator(agent_type=agent_type, api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing calculator: {str(e)}")
        return None

def calculate_with_steps(orchestrator, expression, agent_type):
    """Calculate expression and capture steps using string IO capture."""
    # Create a StringIO object to capture stdout
    f = io.StringIO()
    
    # Use contextlib to redirect stdout to our StringIO object
    with contextlib.redirect_stdout(f):
        try:
            # Calculate the expression
            result = orchestrator.calculate(expression)
        except Exception as e:
            return None, [], str(e)
    
    # Get the captured output
    output = f.getvalue()
    
    # Process the output to extract steps
    steps = []
    inside_steps_section = False
    full_output = output.split('\n')
    
    for line in full_output:
        line = line.strip()
        
        # Check for markers
        if line == "--- CALCULATION STEPS BEGIN ---":
            inside_steps_section = True
            continue
        elif line == "--- CALCULATION STEPS END ---":
            inside_steps_section = False
            continue
            
        # Only process lines inside the steps section
        if inside_steps_section and line:
            # Handle step lines (both agent types)
            if line.startswith("Step"):
                if agent_type == "reducing" and "-->" in line:
                    # For reducing agent, include both the calculation and the remaining expression
                    # Format: "Step 1: 5 * 3 = 15 --> remaining expression: 10 + 15 - 8 / 2"
                    steps.append(line)
                else:
                    # For stepwise agent, take the whole step
                    steps.append(line)
            elif line.startswith("Final result:"):
                # This ensures we capture the final result line too
                steps.append(line)
    
    return result, steps, output

# Sidebar
st.sidebar.title("Calculator Agent")
st.sidebar.markdown("Using LLMs to solve mathematical expressions step by step.")

# API key input
api_key = get_api_key()
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", 
                                  help="Enter your OpenAI API key. It will be stored in the session state.")
    if api_key:
        st.session_state.api_key = api_key

# Agent selection
agent_type = st.sidebar.radio(
    "Select Agent Type",
    ["stepwise", "reducing"],
    index=0,
    help="Stepwise: Maintains full expression and previous steps. Reducing: Progressively simplifies the expression."
)

# About section
with st.sidebar.expander("About"):
    st.markdown("""
    This calculator agent uses OpenAI's models to solve mathematical expressions step by step.
    """)

# Main content
st.title("🧮 Calculator Agent")

# Expression input
expression = st.text_input("Enter a mathematical expression", 
                         value="", 
                         help="Example: 10 + 5 * 3 - 8 / 2")

# Calculate button
calculate_button = st.button("Calculate", type="primary")

# Initialize or get the calculation history from session state
if "calculation_history" not in st.session_state:
    st.session_state.calculation_history = []

# Calculate result
if calculate_button and expression:
    orchestrator = create_orchestrator(agent_type, api_key)
    if orchestrator:
        with st.spinner(f"Calculating with {agent_type} agent..."):
            # Calculate and get steps
            result, steps, debug_output = calculate_with_steps(orchestrator, expression, agent_type)
            
            if result is not None:
                # Add the calculation to history
                st.session_state.calculation_history.append({
                    "expression": expression,
                    "result": result,
                    "agent_type": agent_type,
                    "steps": steps,
                    "debug_output": debug_output
                })
                
                # Display the result
                st.success(f"Calculation completed!")
            else:
                st.error(f"Error during calculation: {debug_output}")

# Display calculation history
if st.session_state.calculation_history:
    st.subheader("Current Calculation")
    latest = st.session_state.calculation_history[-1]
    
    st.markdown(f"**Expression:** `{latest['expression']}`")
    st.markdown(f"**Agent Type:** {latest['agent_type']}")
    
    # Display steps
    st.subheader("Steps")
    if not latest['steps']:
        st.warning("No calculation steps were captured.")
    else:
        # Use distinctive, colored boxes for each step
        for step in latest['steps']:
            if step.startswith("Final result:"):
                continue  # Skip final result
                
            if step.startswith("Step"):
                if "-->" in step and latest['agent_type'] == 'reducing':
                    # Format: "Step 1: 5 * 3 = 15 --> remaining expression: 10 + 15 - 8 / 2"
                    parts = step.split("-->")
                    step_number = parts[0].split(":")[0].strip()  # "Step 1"
                    calculation = ":".join(parts[0].split(":")[1:]).strip()  # "5 * 3 = 15"
                    remaining = parts[1].strip()  # "remaining expression: 10 + 15 - 8 / 2"
                    
                    # Display with colored background
                    st.info(f"**{step_number}:** {calculation}\n\n**{remaining}**")
                else:
                    # Regular step (stepwise agent)
                    step_number = step.split(":")[0].strip()  # "Step 1"
                    calculation = ":".join(step.split(":")[1:]).strip()  # "5 * 3 = 15"
                    
                    # Display with colored background
                    st.info(f"**{step_number}:** {calculation}")
            else:
                st.info(step)
    
    # Display the result
    st.markdown(f"<div class='final-result'>Result: {latest['result']}</div>", unsafe_allow_html=True)
    
    # Previous calculations
    if len(st.session_state.calculation_history) > 1:
        st.subheader("Previous Calculations")
        for i, calc in enumerate(reversed(st.session_state.calculation_history[:-1])):
            with st.expander(f"{calc['expression']} = {calc['result']} ({calc['agent_type']})"):
                # Just display a simple summary instead of detailed steps
                st.markdown(f"""<div class="prev-calc-summary">
                    <div><strong>Expression:</strong> <code>{calc['expression']}</code></div>
                    <div><strong>Result:</strong> {calc['result']}</div>
                    <div><strong>Method:</strong> {calc['agent_type']} calculation</div>
                </div>""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Calculator Agent with Streamlit UI | Built with OpenAI")

if __name__ == "__main__":
    # This is used when running the file directly
    pass 