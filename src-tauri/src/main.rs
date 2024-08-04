// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod utils;
mod consts;

use std::fs;
use std::env;
use std::process::Command;
use tauri::RunEvent;
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;

fn start_uvicorn() -> Result<(), String> {
    if consts::IS_WINDOWS {
        Command::new("cmd")
            .current_dir("src/shell")
            .arg("/C")
            .arg(consts::UVICORN_START_SCRIPT_PATH)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    } else {
        Command::new("sh")
            .current_dir("src/shell")
            .arg("-c")
            .arg(consts::UVICORN_START_SCRIPT_PATH)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    }
    Ok(())
}

fn kill_uvicorn(pid: u32) -> Result<(), String> {
    if consts::IS_WINDOWS {
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

    add_close_log(&pid.to_string())?;

    Ok(())
}

fn add_close_log(pid: &str) -> Result<(), String> {
    // Since we are closing the app by killing the process from terminal directly,
    // we need to manually add a log entry to the log file to indicate that the server
    // was stopped by closing the app. If you think there is a better way to handle this,
    // please feel free to make a PR because I don't like this "solution".
    let now = Local::now();
    let level = "INFO";
    let message = format!("Server stopped by closing the application | PID: {}", pid);
    let log_entry = format!("{} - {} - {}\n", now.format("%Y-%m-%d %H:%M:%S,%3f"), level, message);

    let mut file = OpenOptions::new()
        .append(true)
        .create(true)
        .open(utils::build_home_path(consts::UVICORN_LOG_FILE_PATH))
        .map_err(|err| format!("Failed to open log file: {}", err))?;

    file.write_all(log_entry.as_bytes())
        .map_err(|err| format!("Failed to write to log file: {}", err))?;

    Ok(())
}

fn read_pid_file() -> Result<u32, String> {
    let pid_content = fs::read_to_string(
        utils::build_home_path(consts::UVICORN_PID_FILE_PATH)
    ).map_err(|err| format!("Failed to read PID file: {}", err))?;
    pid_content.trim().parse().map_err(|err| format!("Failed to parse PID: {}", err))
}

fn remove_pid_file() -> Result<(), String> {
    fs::remove_file(
        utils::build_home_path(consts::UVICORN_PID_FILE_PATH)
    ).map_err(|err| format!("Failed to remove PID file: {}", err))
}

#[tauri::command]
fn get_server_url() -> String {
    let url = fs::read_to_string(
        utils::build_home_path(consts::UVICORN_URL_FILE_PATH)
    ).unwrap_or_else(|_| "http://127.0.0.1:8000".to_string());
    url.trim().to_string()
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_server_url])
        .build(tauri::generate_context!())
        .expect("Error building app")
        .run(move |_app_handle, event| match event {
            RunEvent::Ready => {
                start_uvicorn().ok();
            }
            RunEvent::ExitRequested { api, .. } => {
                api.prevent_exit();
                if let Ok(pid) = read_pid_file() {
                    if let Ok(_) = kill_uvicorn(pid) {
                        remove_pid_file().ok();
                    }
                }
                std::process::exit(0);
            }
            _ => {}
        });
}
