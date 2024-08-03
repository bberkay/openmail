// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod utils;
mod constants;

use std::fs;
use std::env;
use std::process::Command;
use tauri::RunEvent;
use chrono::Local;
use std::fmt::Write as FmtWrite;

fn start_uvicorn() -> Result<(), String> {
    if constants::IS_WINDOWS {
        Command::new("cmd")
            .current_dir("src/shell")
            .arg("/C")
            .arg(constants::UVICORN_START_SCRIPT)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    } else {
        Command::new("sh")
            .current_dir("src/shell")
            .arg("-c")
            .arg(constants::UVICORN_START_SCRIPT)
            .spawn()
            .map_err(|err| format!("Failed to start Python server: {}", err))?;
    }
    Ok(())
}

fn kill_uvicorn(pid: u32) -> Result<(), String> {
    if constants::IS_WINDOWS {
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
    let mut log_entry = String::new();
    let now = Local::now();
    let level = "INFO";
    let message = "Server stopped by closing the application | PID: ".to_owned() + pid;
    writeln!(log_entry, "{} - {} - {}", now.format("%Y-%m-%d %H:%M:%S,%3f"), level, message)
        .map_err(|err| format!("Failed to format log message: {}", err))?;

    fs::write(utils::build_home_path(constants::UVICORN_LOG_FILE), log_entry)
        .map_err(|err| format!("Failed to write to log file: {}", err))?;

    Ok(())
}

fn read_pid_file() -> Result<u32, String> {
    let pid_content = fs::read_to_string(
        utils::build_home_path(constants::UVICORN_PID_FILE)
    ).map_err(|err| format!("Failed to read PID file: {}", err))?;
    pid_content.trim().parse().map_err(|err| format!("Failed to parse PID: {}", err))
}

fn remove_pid_file() -> Result<(), String> {
    fs::remove_file(
        utils::build_home_path(constants::UVICORN_PID_FILE)
    ).map_err(|err| format!("Failed to remove PID file: {}", err))
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
