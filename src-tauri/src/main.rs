// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::fs;
use std::env;
use std::process::Command;
use tauri::RunEvent;

const IS_WINDOWS: bool = cfg!(target_os = "windows");
const UVICORN_START_SCRIPT: &str = if IS_WINDOWS { "./windows/start_uvicorn.bat" } else { "./linux/start_uvicorn.sh" };
const UVICORN_PID_FILE: &str = "/.openmail/uvicorn.pid";

fn start_uvicorn() -> Result<(), String> {
    if IS_WINDOWS {
        Command::new("taskkill")
            .current_dir("src/shell")
            .arg("/C")
            .arg(UVICORN_START_SCRIPT)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    } else {
        Command::new("sh")
            .current_dir("src/shell")
            .arg("-c")
            .arg(UVICORN_START_SCRIPT)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    }
    Ok(())
}

fn kill_uvicorn(pid: u32) -> Result<(), String> {
    if IS_WINDOWS {
        Command::new("taskkill")
            .arg("/PID")
            .arg(pid.to_string())
            .arg("/F")
            .status()
            .map_err(|err| format!("Failed to kill process: {}", err))?;
    } else {
        Command::new("kill")
            .arg("-TERM")
            .arg(pid.to_string())
            .status()
            .map_err(|err| format!("Failed to kill process: {}", err))?;
    }
    Ok(())
}

fn get_pid_file_path() -> String {
    format!("{}/{}", env::var("HOME").unwrap(), UVICORN_PID_FILE)
}

fn read_pid_from_file() -> Result<u32, String> {
    let pid_content = fs::read_to_string(get_pid_file_path()).map_err(|err| format!("Failed to read PID file: {}", err))?;
    pid_content.trim().parse().map_err(|err| format!("Failed to parse PID: {}", err))
}

fn remove_pid_file() -> Result<(), String> {
    fs::remove_file(get_pid_file_path()).map_err(|err| format!("Failed to remove PID file: {}", err))
}

fn main() {
    tauri::Builder::default()
        .build(tauri::generate_context!())
        .expect("Error building app")
        .run(move |_app_handle, event| match event {
            RunEvent::Ready => {
                start_uvicorn().ok();
            }
            RunEvent::ExitRequested { api, .. } => {
                api.prevent_exit();
                if let Ok(pid) = read_pid_from_file() {
                    if let Ok(_) = kill_uvicorn(pid) {
                        remove_pid_file().ok();
                    }
                }
                std::process::exit(0);
            }
            _ => {}
        });
}
