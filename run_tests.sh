#!/bin/bash

# Load the API key from .env file
export $(grep -v '^#' .env | xargs)

# Print environment variables for debugging
echo "Environment variables:"
echo "OPENAI_API_KEY='${OPENAI_API_KEY:0:8}...'"

# Run the tests
python3 tests/orchestrator_tests.py 