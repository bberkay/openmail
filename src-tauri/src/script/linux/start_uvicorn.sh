#!/bin/bash

echo "Starting server..."

cd ../server
source ".venv/bin/activate"
python "main.py"
