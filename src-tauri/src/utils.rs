use std::env;

pub fn build_home_path(file: &str) -> String {
    format!("{}/{}", env::var("HOME").unwrap(), file)
}
