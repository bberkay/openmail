# Openmail – Installation Guide

This document describes the installation and setup process for Openmail.

Openmail consists of two components:
- Openmail App – the client application (referred to as app in this guide)
- Openmail Server – the backend service (referred to as server in this guide)

## Downloads

All builds are automatically published in each [GitHub Release](../../releases) after tagging a version (e.g. `v0.0.1-alpha0`).
Each release contains the following assets:

| Platform                 | Component | File Name                                   |
| ------------------------ | --------- | ------------------------------------------- |
| Windows              | Server             | `Openmail-Server_v0.0.1-alpha0_windows.exe` |
| Windows                  | App              | `Openmail_v0.0.1-alpha0_windows.exe`        |
| macOS (Intel)        | Server          | `Openmail-Server_v0.0.1-alpha0_macos-x64`   |
| macOS (Apple Silicon)    | Server            | `Openmail-Server_v0.0.1-alpha0_macos-arm64` |
| macOS (Intel)            | App                 | `Openmail_v0.0.1-alpha0_macos-x64.dmg`      |
| macOS (Apple Silicon)    | App               | `Openmail_v0.0.1-alpha0_macos-arm64.dmg`    |
| Linux (Universal)        | Server           | `Openmail-Server_v0.0.1-alpha0_linux`       |
| Linux (Debian-based) | App               | `Openmail_v0.0.1-alpha0_linux-amd64.deb`    |
| Linux (Red Hat-based)    | App               | `Openmail_v0.0.1-alpha0_linux-amd64.rpm`    |
| Linux (Universal)        | App            | `Openmail_v0.0.1-alpha0_linux.AppImage`     |


## Installation

### Server
  * [Windows](#windows)
  * [macOS (Intel-based or Apple Silicon)](#macos-intel--apple-silicon)
  * [Debian-Based Linux](#debian-based-linux-ubuntu-mint)
  * [Red Hat-Based Linux](#red-hat-based-fedora-rhel)
  * [Other Linux Distributions](#other-linux-distributions)
### App
  * [Windows](#windows-1)
  * [macOS (Intel-based or Apple Silicon)](#macos-intel--apple-silicon-1)
  * [Debian-Based Linux](#debian-based-linux-ubuntu-mint-1)
  * [Red Hat-Based Linux](#red-hat-based-fedora-rhel-1)
  * [Other Linux Distributions](#other-linux-distributions-1)

## Server Installation

### Windows

1. Download **`Openmail-Server_v0.0.1-alpha0_windows.exe`**.
2. Run the executable.
3. The server will start immediately.
4. Continue to install [app](#windows-1)

### macOS (Intel & Apple Silicon)

1. Download the correct file for your chipset:
   * **Intel:** `Openmail-Server_v0.0.1-alpha0_macos-x64`
   * **Apple Silicon (M1/M2/M3):** `Openmail-Server_v0.0.1-alpha0_macos-arm64`
2. Make it executable:
   ```bash
   chmod +x Openmail-Server_v0.0.1-alpha0_macos-*
   ```
3. Run it:
   ```bash
   ./Openmail-Server_v0.0.1-alpha0_macos-*
   ```
4. Continue to install [app](#macos-intel--apple-silicon-1)

### Debian-Based Linux (Ubuntu, Mint...)

1. Download:
   ```
   Openmail-Server_v0.0.1-alpha0_linux-amd64.deb
   ```
2. Install:
   ```bash
   sudo dpkg -i Openmail-Server_v0.0.1-alpha0_linux-amd64.deb
   ```
3. Start the server:
   ```bash
   openmail-server
   ```
4. Continue to install [app](#debian-based-linux-ubuntu-mint-1)

### Red Hat-Based (Fedora, RHEL...)

1. Download:
   ```
   Openmail-Server_v0.0.1-alpha0_linux-amd64.rpm
   ```
2. Install:
   ```bash
   sudo rpm -i Openmail-Server_v0.0.1-alpha0_linux-amd64.rpm
   ```
3. Run:
   ```bash
   openmail-server
   ```
4. Continue to install [app](#red-hat-based-fedora-rhel-1)

### Other Linux Distributions

1. Download the standalone binary:
   ```
   Openmail-Server_v0.0.1-alpha0_linux
   ```
2. Make executable:
   ```bash
   chmod +x Openmail-Server_v0.0.1-alpha0_linux
   ```
3. Run:
   ```bash
   ./Openmail-Server_v0.0.1-alpha0_linux
   ```
4. Continue to install [app](#other-linux-distributions-1)

## App Installation

### Windows

1. Download **`Openmail_v0.0.1-alpha0_windows.exe`**.
2. Run the installer.
3. Launch **Openmail** from Start Menu or Desktop.
4. Continue with [configuration](#configuration).

### macOS (Intel & Apple Silicon)

1. Download the appropriate DMG:
   * **Intel:** `Openmail_v0.0.1-alpha0_macos-x64.dmg`
   * **Apple Silicon (arm):** `Openmail_v0.0.1-alpha0_macos-arm64.dmg`
2. Open the `.dmg`.
3. Drag **Openmail.app** into Applications.
4. Open it (you may need to right-click → Open for Gatekeeper).
5. Continue with [configuration](#configuration).

### Debian-Based Linux (Ubuntu, Mint…)

1. Download:
   ```
   Openmail_v0.0.1-alpha0_linux-amd64.deb
   ```
2. Install:
   ```bash
   sudo dpkg -i Openmail_v0.0.1-alpha0_linux-amd64.deb
   ```
3. Launch:
   ```bash
   openmail
   ```
4. Continue with [configuration](#configuration).

### Red Hat-Based (Fedora, RHEL…)

1. Download:
   ```
   Openmail_v0.0.1-alpha0_linux-amd64.rpm
   ```
2. Install:
   ```bash
   sudo rpm -i Openmail_v0.0.1-alpha0_linux-amd64.rpm
   ```
3. Launch:
   ```bash
   openmail
   ```
4. Continue with [configuration](#configuration).

### Other Linux Distributions

1. Download the AppImage:
   ```
   Openmail_v0.0.1-alpha0_linux.AppImage
   ```
2. Make it executable:
   ```bash
   chmod +x Openmail_v0.0.1-alpha0_linux.AppImage
   ```
3. Launch:
   ```bash
   ./Openmail_v0.0.1-alpha0_linux.AppImage
   ```
4. Continue with [configuration](#configuration).

## Configuration

> [!NOTE]
> The server currently has no graphical interface or dashboard, so you
need to restart it to change the configuration.

1- When you start the server, you’ll be prompted to enter the host and port
(and some other things too) where the API should run.
2- When you launch the app, configure the same host and port during the initial setup
(or later via the Settings page) so it can connect to your running server.
3- Once the app is connected to the server, you can add your email accounts and start
exploring everything Openmail offers.

## Building from Source (Optional)

If you prefer to build manually:

```bash
# Server
cd server
uv sync
uv pip install pyinstaller
uv run pyinstaller --onefile --name openmail-server --paths=. src/main.py
# Server build outputs will be in ./dist/openmail-server

# App
cd app
bun install
bun tauri build
# App build outputs will be in ./app/src-tauri/target/release/bundle/
```

## Updating

> [!WARNING]
> Openmail does **not currently have auto-update feature.**

1. Go to the [latest release](../../releases/latest) page on GitHub.
2. Download the latest **app** and **server** builds for your operating system.
3. Replace your existing `openmail` app and `openmail-server` files with the new ones.
4. Restart both to complete the update.

## Troubleshooting

### 1. PyInstaller Not Building the Server

If the server build fails and PyInstaller cannot find your virtual environment or dependencies, try these steps instead of using `uv run pyinstaller`:

```bash
uv pip install pyinstaller

# Verify PyInstaller is detected from the current .venv
which pyinstaller  # should point inside .venv/bin/

# If pyinstaller is NOT in the .venv then:
# you can try to install it within the .venv like
source .venv/bin/activate # or .venv\Scripts\Activate for windows
uv pip install pyinstaller
pyinstaller --onefile --name openmail-server --paths=. src/main.py

# If pyinstaller is IN the .venv then:
uv pip install pyinstaller
uv run pyinstaller --onefile --name openmail-server --paths=. src/main.py
```

---

### 2. App Build Fails on Arch Linux (or other linux distributions)

If the App build fails on Arch Linux (for example, during AppImage packaging), try the following fixes:

```bash
rm -f ~/.cache/tauri/linuxdeploy-x86_64.AppImage
yay -S linuxdeploy
sudo pacman -S appstream desktop-file-utils fuse2 --needed

# Prevent stripping of binaries (may fix AppImage build issues)
export NO_STRIP=true

# Rebuild the App
bun tauri build
```

---

**Enjoy using Openmail! Feel free to contributing**
