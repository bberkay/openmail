// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Child, Command};
use std::sync::{Arc, Mutex};
use tauri::RunEvent;

const IS_WINDOWS: bool = cfg!(target_os = "windows");
const COMMAND: &str = if IS_WINDOWS { "cmd" } else { "sh" };
const ARGUMENT_FLAG: &str = if IS_WINDOWS{ "/C" } else { "-c" };
const UVICORN_START_SCRIPT: &str = if IS_WINDOWS { "./windows/start_uvicorn.bat" } else { "./linux/start_uvicorn.sh" };

fn start_python_server() -> Result<Child, String> {
    let child = Command::new(COMMAND)
    .current_dir("src/server/shell")
    .arg(ARGUMENT_FLAG)
    .arg(UVICORN_START_SCRIPT)
    .spawn()
    .map_err(|err| format!("Failed to start Python server: {}", err))?;

    Ok(child)
}

fn main() {
    let child_process = Arc::new(Mutex::new(None));
    tauri::Builder::default()
        .build(tauri::generate_context!())
        .expect("Error building app")
        .run(move |_app_handle, event| match event {
            RunEvent::Ready => {
                let child = start_python_server().expect("Failed to start Python server");
                *child_process.lock().unwrap() = Some(child);
            }
            RunEvent::ExitRequested { api, .. } => {
                api.prevent_exit();
                if let Some(mut child) = child_process.lock().unwrap().take() {
                    let _ = child.kill();
                }
                std::process::exit(0);
            }
            _ => {}
        });
}
