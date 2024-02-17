#!/bin/bash

# Set environment variables
export LOGS_PATH=/home/schrutebeet/Desktop/logs/stocks
export DATABASE_HOST=localhost

# Change working directory
cd /home/schrutebeet/Desktop/stock_market

# Set up python environment
source stock_venv/bin/activate

# Run main file
python -m src.main
