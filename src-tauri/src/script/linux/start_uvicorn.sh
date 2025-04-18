#!/bin/bash

echo "Starting server..."

cd ../server
source ".venv/bin/activate"

PYTHONPATH=$(pwd) python main.py
