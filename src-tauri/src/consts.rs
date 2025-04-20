pub const IS_WINDOWS: bool = cfg!(target_os = "windows");
pub const UVICORN_START_SCRIPT_PATH: &str = if IS_WINDOWS {
    "./windows/start_uvicorn.bat"
} else {
    "./linux/start_uvicorn.sh"
};
pub const UVICORN_LOG_FILE_PATH: &str = "/.openmail/server/logs/uvicorn.log";
pub const UVICORN_INFO_FILE_PATH: &str = "/.openmail/server/uvicorn.info";
