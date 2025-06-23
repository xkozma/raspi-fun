#!/bin/bash

# Navigate to the directory containing the Electron app
cd "$(dirname "$0")"
python ./python/assistant.py
# Start the Electron app using npm
npm start