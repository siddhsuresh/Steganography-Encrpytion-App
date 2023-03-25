import { invoke } from "@tauri-apps/api/tauri";
import "./App.css";
import React, { useState } from "react";
import background from "./assets/background.jpg";
  
function App() {
    const [file, setFile] = useState();
    function handleChange(e) {
        console.log(e.target.files);
        setFile(URL.createObjectURL(e.target.files[0]));
    }
  
    return (
        <div className="App" style={{ backgroundImage: `url(${background})`,height:"100vh",backgroundRepeat:"no-repeat",backgroundSize:"cover"}}>
          <h1>Welcome to our Steganography App!!!</h1>
            <h2>Add Image:</h2>
            <input type="file" onChange={handleChange} />
            <img src={file} />
        </div>
    );
}
  
export default App;
  

