import "./App.css";
import { useState } from "react";
import Dropzone from "./components/Dropzone";
import {
  Avatar,
  Button,
  createStyles,
  Image,
  rem,
  TextInput,
} from "@mantine/core";

const useStyles = createStyles((theme) => ({
  body: {
    position: "relative",
    top: -120,
    padding: "10px",
    height: "100vh",
    width: "100vw",
  },
  wrapper: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    border: "1px solid black",
  },
  image: {
    marginLeft: rem(30),
    marginRight: rem(30),
  },
}));
function App() {
  const { classes, theme } = useStyles();
  const [isImage, setIsImage] = useState(false);
  function submit() {
    setIsImage(true);
  }
  return (
    <div className={classes.body}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <h2
          style={{
            margin: rem(30),
          }}
        >
          Upload the original image and the secret message
        </h2>
        <div
          style={{
            width: "60%",
            display: "flex",
            justifyContent: "space-around",
            // borderRadius: "41px",
            // background: "#e0e0e0",
            // boxShadow:  "5px 5px 28px #c1c1c1,  -5px -5px 28px #ffffff",
            padding: rem(10),
          }}
        >
          <Dropzone />
          <TextInput
            placeholder="Enter Message Here"
            size="xl"
            radius="md"
            withAsterisk
          />
        </div>
      </div>
      <div
        className="display"
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: "10px",
          margin: rem(30),
        }}
      >
        <div>
          <h3>Original Image</h3>
          <Image height={300} fit="contain" src="/src/assets/lena.jpg" />
        </div>
        <Button
          style={{
            height: "3rem",
            // width: "3rem",
            borderRadius: "20px",
          }}
        >
          <Avatar
            src="/src/assets/encrypt-icon.jpg"
            style={
              {
                // height: "1rem",
                // width:"2rem"
              }
            }
          />
        </Button>
        <div>
          <h3>Steganographic Image</h3>
          <Image height={300} fit="contain" src="/src/assets/lena.jpg" />
        </div>
      </div>
    </div>
  );
}

export default App;
