import { invoke } from "@tauri-apps/api/tauri";
import "./App.css";
import React, { useState } from "react";
import Header from "./Header";
import Dropzone from "./Dropzone";
import { Avatar, BackgroundImage, Button, createStyles, Image, rem } from '@mantine/core';
import Hero from "./Hero";
import ImageDisplay from "./ImageDisplay";
const links= [
    { "link": "/about", "label": "Features" },
    { "link": "/pricing", "label": "Pricing" },
    { "link": "/learn", "label": "Learn" },
    { "link": "/community", "label": "Community" }
]

  const useStyles = createStyles((theme) => ({
    body:{
        padding: 0,
        margin: 0,
        height: '100vh',
        width: '100vw',
    },
    wrapper: {
      display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid black',
        
    },
    image:{
        marginLeft: rem(30),
        marginRight: rem(30),

    }
  }));
function App() {
    const { classes, theme } = useStyles();
    const [isImage, setIsImage] = useState(false);
    function submit(){
        setIsImage(true);
    }
    return (
        <div className={classes.body}>
            <Header links={links}/>
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
            }}>
              <Hero />
              <div className="content">
                <Dropzone />
                {/* <Image className={classes.image} width={900} height={600} src="./assets/lena.jpg" /> */}
              </div>
            </div>
            <div className="display" style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'center',
                gap: "10px",
                margin: rem(30),
            }}>
              <Image  height={500} fit="contain" src="/src/assets/lena.jpg" />
              <Button style={{
                height: "3rem",
                // width: "3rem",
                borderRadius: "20px",
              }}><Avatar src="/src/assets/encrypt-icon.jpg" style={{
                // height: "1rem",
                // width:"2rem"
              }} />
              </Button>
              <Image  height={500} fit="contain" src="/src/assets/lena.jpg" />
            </div>
        </div>
    );
}
  
export default App;
  

