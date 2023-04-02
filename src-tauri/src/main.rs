// use std::process::Command;
// use std::fs::File;
// use base64;
// use chrono;

// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

// fn get_image(
//     image: String,
//     file_name: String,
//     file_extension: String,
//     file_path: String,
// ) -> String {
//     let mut file_path = file_path;
//     let mut file_name = file_name;
//     let mut file_extension = file_extension;
//     let mut image = image;
//     image = image.replace("data:image/png;base64,", "");
//     file_path.push_str(&file_name);
//     file_path.push_str(&file_extension);
//     let mut file = match File::create(&file_path) {
//         Err(why) => panic!("couldn't create {}: {}", file_path, why),
//         Ok(file) => file,
//     };
//     let decoded = base64::decode(&image).unwrap();
//     match file.write_all(&decoded) {
//         Err(why) => panic!("couldn't write to {}: {}", file_path, why),
//         Ok(_) => println!("successfully wrote to {}", file_path),
//     }
// }

#[tauri::command]
fn stegano(image:String,) -> Result<String, String> {
    // let file_name = chrono::offset::Local::now()::timestamp().to_string();
    let file_extension = ".png";
    let file_path = "./tmp/";
    let image_path = get_image(image, file_name.to_string(), file_extension.to_string(), file_path.to_string());
    let script_path = "./src/python/main.py";
    let mut child = Command::new("python3")
        .arg(script_path)
        .arg(image_path)
        .spawn()
        .expect("failed to execute process");
    let output = child.wait_with_output().expect("failed to wait on child");
    println!("output: {}", String::from_utf8(output.stdout).unwrap());
    Ok(String::from_utf8(output.stdout).unwrap())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}