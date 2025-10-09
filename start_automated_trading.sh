#!/bin/bash

echo "Starting Automated Trading System..."
echo ""
echo "This will run continuously and monitor markets automatically."
echo "Press Ctrl+C to stop the system."
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the automated trading scheduler
python trading_scheduler.py