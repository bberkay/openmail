@echo off
cd ..\server
python3 -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
deactivate

echo "Virtual environment created successfully."