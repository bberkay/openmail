# Openmail – Installation Guide

This document describes the installation and setup process for Openmail.

Openmail consists of two components:
- Openmail App – the client application (referred to as app in this guide)
- Openmail Server – the backend service (referred to as server in this guide)

---

## Downloads

> [!WARNING]
> Currently, only the Linux AppImage build is available. Additional distribution formats and platform-specific packages will be added in future releases.

All builds are automatically published in each [GitHub Release](../../releases) after tagging a version (e.g. `v1.0.0`).
Each release contains the following assets:

| Platform   | Component        | File                                                                    |
| ---------- | ---------------- | ----------------------------------------------------------------------- |
| 🪟 Windows | App   | `Openmail_v1.0.0_windows.exe` |
| 🪟 Windows | Server | `Openmail-Server_v1.0.0_windows.exe` |
| 🐧 Linux   | App   | `Openmail_v1.0.0_linux.AppImage` |
| 🐧 Linux   | Server | `Openmail-Server_v1.0.0_linux` |

---

## Windows Installation

### 1. Server

1. Download `Openmail-Server_v1.0.0_windows.exe` from the [latest release](../../releases/latest) (mostly in your server).
2. Run the executable — it will start a FastAPI web server.
3. [Configure server](#configuration).

### 2. App

1. Download `Openmail_v1.0.0_windows.exe` from the [latest release](../../releases/latest) (in your computer).
2. Run the executable.
3. Launch **Openmail** from the Start Menu or Desktop shortcut.
4. [Configure app](#configuration).

---

## Linux Installation

### 1. Server

1. Download `Openmail-Server_v1.0.0_linux`.
2. Make the binary executable:

   ```bash
   chmod +x Openmail-Server_*
   ```
3. Run the server:

   ```bash
   ./Openmail-Server_*
   ```
4. [Configure server](#configuration).

### 2. App (AppImage)

1. Download `Openmail_v1.0.0_linux.AppImage`.
2. Make the AppImage executable:

   ```bash
   chmod +x Openmail_*.AppImage
   ```
3. Run it directly:

   ```bash
   ./Openmail_*.AppImage
   ```
4. [Configure app](#configuration).

---

## Configuration

> [!NOTE]
> The server currently has no graphical interface or dashboard.
You can set configuration values through environment variables before starting the server.
Check out the [.env.example](../../server/.env.example)

1- When you start the server, you’ll be prompted to enter the host and port where
the API should run.
2- When you launch the app, configure the same host and port during the initial setup
(or later via the Settings page) so it can connect to your running server.
3- Once the app is connected to the server, you can add your email accounts and start
exploring everything Openmail offers.

---

## Building from Source (Optional)

If you prefer to build manually:

```bash
# Server
cd server
uv sync
source .venv\bin\activate # or .venv\Scripts\activate in windows
pyinstaller --onefile --name openmail-server --paths=. src/main.py

# App
cd app
bun install
bun tauri build
```

## Updating

> [!WARNING]
> Openmail does **not currently have auto-update feature.**

1. Go to the [latest release](../../releases/latest) page on GitHub.
2. Download the latest **app** and **server** builds for your operating system.
3. Replace your existing `openmail` app and `openmail-server` files with the new ones.
4. Restart both to complete the update.

---

## Troubleshooting

### 1. PyInstaller Not Building the Server

If the server build fails and PyInstaller cannot find your virtual environment or dependencies, try these steps instead of using `uv run pyinstaller`:

```bash
uv pip install pyinstaller
source .venv/bin/activate

# Verify PyInstaller is detected from the current .venv
which pyinstaller  # should point inside .venv/bin/

# Build the server executable
pyinstaller --onefile --name openmail-server --paths=. src/main.py
```

> **Note:**
> This ensures that PyInstaller correctly packages all dependencies from your `.venv`'s `site-packages` directory.

---

### 2. App Build Fails on Arch Linux

If the App build fails on Arch Linux (for example, during AppImage packaging), try the following fixes:

```bash
yay -S linuxdeploy
sudo pacman -S appstream desktop-file-utils fuse2 --needed

# Prevent stripping of binaries (may fix AppImage build issues)
export NO_STRIP=true

# Rebuild the App
bun tauri build
```

> **Tip:**
> Missing `fuse2` or `linuxdeploy` are common causes of Tauri build failures on Arch-based systems.


---

**Enjoy using Openmail! Feel free to contributing**
