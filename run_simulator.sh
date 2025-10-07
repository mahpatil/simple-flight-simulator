#!/bin/bash

# Simple Flight Simulator Launch Script

echo "Starting Simple Flight Simulator..."
echo "======================================"

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment and run the simulator
./.venv/bin/python src/main.py