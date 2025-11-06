#!/usr/bin/env bash
set -e

# Check for uv
if ! command -v uv &> /dev/null; then
  echo "Error: uv not found. Please install uv: https://github.com/astral-sh/uv"
  exit 1
fi

# Check for Bun
if ! command -v bun &> /dev/null; then
  echo "Error: Bun not found. Please install Bun first: https://bun.sh"
  exit 1
fi

# Check for Rustup (needed for Tauri)
if ! command -v rustup &> /dev/null; then
  echo "Error: Rust not found but required for tauri. Please install Rust:"
  echo "       https://tauri.app/start/prerequisites/#rust"
  exit 1
fi

echo "Installing Openmail Server..."
cd server
uv sync  # or `uv pip install -r requirements.txt`
cd ..
echo "Openmail server installation complete!"

echo "Installing Openmail App..."
cd app
bun install
cd ..
echo "Openmail installation complete!"

echo "To run the server: cd server && uv run -m src.main"
echo "To run the tests:  cd server && uv run -m unittest tests.dir.file_name.ClassName"
echo "To run the app:    cd app && bun run tauri dev"
