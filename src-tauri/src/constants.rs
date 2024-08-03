pub const IS_WINDOWS: bool = cfg!(target_os = "windows");
pub const UVICORN_START_SCRIPT: &str = if IS_WINDOWS { "./windows/start_uvicorn.bat" } else { "./linux/start_uvicorn.sh" };
pub const UVICORN_LOG_FILE: &str = "/.openmail/logs/uvicorn.log";
pub const UVICORN_PID_FILE: &str = "/.openmail/uvicorn.pid";
