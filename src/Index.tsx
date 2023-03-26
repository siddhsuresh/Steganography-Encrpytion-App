import { invoke } from "@tauri-apps/api/tauri";
import "./App.css";
import React, { useState } from "react";
import {createStyles, rem } from '@mantine/core';
import Hero from "./components/Hero";

  const useStyles = createStyles((theme) => ({
    body:{
        padding: 0,
        margin: 0,
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
export default function Index() {
    const { classes, theme } = useStyles();
    const [isImage, setIsImage] = useState(false);
    function submit(){
        setIsImage(true);
    }
    return (
        <div className={classes.body}>
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
            }}>
              <Hero />
            </div>
        </div>
    );
}  

