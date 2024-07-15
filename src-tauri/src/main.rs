// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::thread;
use std::io::{BufRead, BufReader};

const PYTHON_SERVER_DIR: &str = "src/server";
const PYTHON_SERVER_MODULE: &str = "main:app";

fn start_python_server() -> Result<String, String> {
    println!("Python server starting...");
    let mut child = Command::new("uvicorn")
        .current_dir(PYTHON_SERVER_DIR)
        .arg(PYTHON_SERVER_MODULE)
        .arg("--reload")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;

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

    Ok("Python server started".to_string())
}

#[tauri::command]
fn hello() -> String {
    "Hello from Rust!".to_string()
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            hello
        ])
        .setup(|_app| {
            // Start the python server
            start_python_server().expect("Failed to start python server");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

