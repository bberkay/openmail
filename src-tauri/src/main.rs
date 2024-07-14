// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};

const PYTHON_SCRIPT_PATH: &str = "./src/python_scripts/main.py";

fn run_python_script(operation: &str, params: Vec<&str>) -> Result<String, String> {
    println!("Running python script with operation: {} and params: {:?}", operation, params);
    let child = Command::new("python")
        .arg(PYTHON_SCRIPT_PATH)
        .arg(operation)
        .args(params)
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

#[tauri::command]
async fn login(email: &str, password: &str) -> Result<String, String> {
    run_python_script("login", vec![email, password])
}

#[tauri::command]
async fn get_emails(folder: &str, search: &str, offset: &str) -> Result<String, String> {
    run_python_script("get_emails", vec![folder, search, offset])
}

#[tauri::command]
async fn get_email_content(id: &str) -> Result<String, String> {
    run_python_script("get_email_content", vec![id])
}

#[tauri::command]
async fn get_folders() -> Result<String, String> {
    run_python_script("get_folders", vec![])
}

#[tauri::command]
async fn mark_email(id: &str, mark: &str, folder: &str) -> Result<String, String> {
    run_python_script("mark_email", vec![id, mark, folder])
}

#[tauri::command]
async fn delete_email(id: &str, folder: &str) -> Result<String, String> {
    run_python_script("delete_email", vec![id, folder])
}

#[tauri::command]
async fn move_email(id: &str, source: &str, destination: &str) -> Result<String, String> {
    run_python_script("move_email", vec![id, source, destination])
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            login, 
            get_emails, 
            get_email_content, 
            get_folders, 
            mark_email, 
            delete_email,
            move_email
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

