install:
	./install.sh

run-server:
	cd server && uv run main.py

run-app:
	cd app && bun tauri dev
