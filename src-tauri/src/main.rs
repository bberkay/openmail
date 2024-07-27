// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use tauri::RunEvent;

const PYTHON_SERVER_DIR: &str = "server";
const PYTHON_SERVER_MODULE: &str = "main:app";

fn start_python_server() -> Result<Child, String> {
    println!("Python server starting...");
    let mut child = Command::new("uvicorn")
        .current_dir(PYTHON_SERVER_DIR)
        .arg(PYTHON_SERVER_MODULE)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|err| format!("Failed to start Python server: {}", err))?;

    let stdout = child.stdout.take().ok_or("Failed to capture stdout")?;
    let stderr = child.stderr.take().ok_or("Failed to capture stderr")?;

    // Spawning a new thread to read stdout
    thread::spawn(move || {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            match line {
                Ok(line) => println!("STDOUT: {}", line),
                Err(err) => eprintln!("Error reading stdout: {}", err),
            }
        }
    });

    // Spawning a new thread to read stderr
    thread::spawn(move || {
        let reader = BufReader::new(stderr);
        for line in reader.lines() {
            match line {
                Ok(line) => eprintln!("STDERR: {}", line),
                Err(err) => eprintln!("Error reading stderr: {}", err),
            }
        }
    });

    Ok(child)
}

fn main() {
    //let child_process = Arc::new(Mutex::new(None));

    tauri::Builder::default()
        .build(tauri::generate_context!())
        .expect("Error building app")
        .run(move |app_handle, event| match event {
            RunEvent::Ready => {
                /*let child = start_python_server().expect("Failed to start Python server");
                 *child_process.lock().unwrap() = Some(child);*/
            }
            RunEvent::ExitRequested { api, .. } => {
                /*api.prevent_exit();
                if let Some(mut child) = child_process.lock().unwrap().take() {
                    println!("Python server stopping...");
                    let _ = child.kill();
                }
                std::process::exit(0);*/
            }
            _ => {}
        });
}
