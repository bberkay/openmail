install:
	./install.sh

run-server:
	cd server && uv run -m src.main.py

run-app:
	cd app && bun run tauri dev
