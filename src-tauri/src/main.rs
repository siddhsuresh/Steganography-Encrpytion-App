// use std::process::Command;
// use std::fs::File;

// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use chrono;
use std::fs::File;
use std::io::prelude::*;
use rsa::{RsaPublicKey, pkcs1::DecodeRsaPublicKey};
use base64::{
    alphabet,
    engine::{self, general_purpose},
    Engine as _,
};

use tauri::{Manager, Window};

// the payload type must implement `Serialize` and `Clone`.
#[derive(Clone, serde::Serialize)]
struct Payload {
  message: String,
}

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
// create an image from a base64 string and save it to the app's data folder
fn save_image(window: Window,image: &str) -> Result<String, String> {
    let mut image = image.to_string();
    image.retain(|c| !c.is_whitespace());
    // println!("Image: {:?}", image);
    //remove the data:image/png;base64, part of the string
    image = image.replace("data:image/png;base64,", "");
    //remove the data:image/jpeg;base64, part of the string
    image = image.replace("data:image/jpeg;base64,", "");
    // remove the data:image/jpg;base64, part of the string
    image = image.replace("data:image/jpg;base64,", "");
    // convert base64 string to bytes
    let image = general_purpose::STANDARD.decode(image).unwrap();
    // println!("Image: {:?}", image);
    let now = chrono::Local::now();
    let filename = format!("{}.png", now.format("%Y-%m-%d_%H-%M-%S"));
    let path = "/home/siddharth/Projects/Crypto/store/";
    let path = format!("{}{}", path, filename);
    // println!("Saving image to {:?}", path);
    let mut file = File::create(path.clone()).unwrap();
    file.write_all(&image).unwrap();
    println!("Saved image to {:?}", path);
    std::thread::spawn(move || {
        window
            .emit(
                "event-name",
                Payload {
                    message: "Image saved!".into(),
                },
            )
            .unwrap();
    });
    Ok(path.to_string().into())
}

#[tauri::command]
fn steganography(path: &str, message: &str, pass: &str, app: tauri::AppHandle) -> Result<(), String> {
    let path = path.to_string();
    let message = message.to_string();
    let output_path = path.replace(".png", "_output.png");
    let pass = pass.to_string();
    // make a copy of output_path
    let output_path_clone = output_path.clone();
    // let mut pem = File::open("/home/siddharth/Projects/Crypto/backend/src/public.pem").unwrap();
    // let public_key = RsaPublicKey::from_pkcs1_pem(pem)?;
    // let encrypted_pass = public_key.encrypt(pass.as_bytes(), &mut rand::thread_rng())?;
    std::thread::spawn(move || {
        let output = std::process::Command::new("python")
            .arg("D:\ Steganography-Encrpytion-App-main\ backend\ src\ main.py")
            .arg("-e")
            .arg(path)
            .arg(output_path)
            .arg(message)
            .arg(pass)
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
        let output = String::from_utf8(output.stdout).unwrap();
        println!("output: {:?}", output);
        // og_signature = output.replace("\n", "");
        // my_vec.push(output);
        app.emit_all("og", Payload {
            message: output,
        }).unwrap();
        // read the output image and send it to the frontend
        let mut file = File::open(
            output_path_clone
        ).unwrap();
        let mut contents = Vec::new();
        file.read_to_end(&mut contents).unwrap();
        let contents = base64::encode(contents);
        let contents = format!("data:image/png;base64,{}", contents);
        app.emit_all("stegImage", Payload {
            message: contents,
        }).unwrap();
    });    
    Ok(())
}

#[tauri::command]
fn decrypt(path: &str, pass: &str, image_sign: &str, app: tauri::AppHandle) -> Result<(), String> {
    let path = path.to_string();
    let pass = pass.to_string();
    let image_sign = image_sign.to_string();
    // let mut pem = File::open("/home/siddharth/Projects/Crypto/backend/src/public.pem").unwrap();
    // let public_key = RsaPublicKey::from_pkcs1_pem(pem)?;
    // let encrypted_pass = public_key.encrypt(pass.as_bytes(), &mut rand::thread_rng())?;
    std::thread::spawn(move || {
        let output = std::process::Command::new("python")
            .arg("D:\ Steganography-Encrpytion-App-main\ backend\ src\ main.py")
            .arg("-d")
            .arg(path)
            .arg(pass)
            .arg(image_sign)
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
        let error = String::from_utf8(output.stderr).unwrap();
        //if there is an error, send it to the frontend
        if error != "" {
            app.emit_all("message", Payload {
                message: "Image or the signature has been tampered with!".into(),
            }).unwrap();
            return;
        } 
        let output = String::from_utf8(output.stdout).unwrap();
        println!("output: {:?}", output);
        // og_signature = output.replace("\n", "");
        // my_vec.push(output);
        app.emit_all("message", Payload {
            message: output,
        }).unwrap();
    });    
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // `main` here is the window label; it is defined on the window creation or under `tauri.conf.json`
            // the default value is `main`. note that it must be unique
            let main_window = app.get_window("main").unwrap();

            // listen to the `event-name` (emitted on the `main` window)
            let id = main_window.listen("event-name", |event| {
                println!("got window event-name with payload {:?}", event.payload());
            });
            // unlisten to the event using the `id` returned on the `listen` function
            // an `once` API is also exposed on the `Window` struct
            main_window.unlisten(id);

            // emit the `event-name` event to the `main` window
            main_window
                .emit(
                    "event-name",
                    Payload {
                        message: "Tauri is awesome!".into(),
                    },
                )
                .unwrap();
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![save_image, steganography, decrypt])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
