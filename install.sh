#!/usr/bin/env bash
set -e

echo "Installing Openmail Server..."

if ! command -v uv &> /dev/null; then
  echo "Error: uv not found. Please install uv: https://github.com/astral-sh/uv"
  exit 1
fi

echo "Setting up Openmail server..."
cd server
uv sync  # or `uv pip install -r requirements.txt`
cd ..
echo "Openmil server installation complete!"

echo "Installing up Openmail..."

if ! command -v bun &> /dev/null; then
  echo "Error: Bun not found. Please install Bun first: https://bun.sh"
  exit 1
fi

echo "Setting up Openmail..."

cd app
bun install
cd ..
echo "Openmil installation complete!"

echo "To run the server: cd server && uv run main.py"
echo "To run the app:    cd app && bun tauri dev"
