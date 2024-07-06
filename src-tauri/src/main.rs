// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet() -> Result<String, String> {
    let mut child = Command::new("python")
        .arg("./src/imap.py")
        .stdout(Stdio::piped())
        .spawn()
        .expect("Failed to start python script");

    let output = child
        .wait_with_output()
        .expect("Failed to read stdout");

    if output.status.success() {
        let result = String::from_utf8(output.stdout).expect("Invalid UTF-8 sequence");
        Ok(result)
    } else {
        let error = String::from_utf8(output.stderr).expect("Invalid UTF-8 sequence");
        Err(error)
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
