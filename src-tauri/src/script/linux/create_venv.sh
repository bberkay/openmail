#!/bin/bash

echo "Creating virtual environment..."

cd ../server
python3 -m venv .venv
source ".venv/bin/activate"
pip install -r requirements.txt
deactivate

echo "Virtual environment created successfully."