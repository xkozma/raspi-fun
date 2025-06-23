#!/bin/bash

# Navigate to the directory containing the Electron app
cd "$(dirname "$0")"
# Check if the Python script can be executed
if ! python ./python/assistant.py; then
    # If it fails, install the required Python packages
    pip install -r ./python/requirements.txt
    # Try to execute the Python script again
    python ./python/assistant.py
fi
# Start the Electron app using npm
npm start