import "./App.css";
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { listen } from "@tauri-apps/api/event";

import { Dropzone, IMAGE_MIME_TYPE, FileWithPath } from "@mantine/dropzone";
import {
  createStyles,
  Image,
  rem,
  SimpleGrid,
  TextInput,
} from "@mantine/core";

const useStyles = createStyles((theme) => ({
  body: {
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
function Decrypt() {
  const { classes } = useStyles();
  const [files, setFiles] = useState<FileWithPath[]>([]);
  const [filePath, setFilePath] = useState<string>("");
  const [ogSign, setogSign] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  useEffect(() => {
    listen("message", (event) => {
      // event.event is the event name (useful if you want to use a single callback fn for multiple event types)
      // event.payload is the payload object
      console.log(event.payload);
      setMessage(event.payload as string);
    }).then((unlisten) => {
      // unlisten() will stop listening to the event
    });
  }, []);
  useEffect(() => {
    const reader = new FileReader();
    const file = files[0];
    if (!file) return;
    reader.readAsDataURL(file);
    reader.onload = function () {
      invoke("save_image", {
        image: reader.result,
      })
        .then((res) => {
          console.log(res);
          setFilePath(res as string);
        })
        .catch((err) => {
          console.log(err);
        });
    };
  }, [files]);

  const previews = files.map((file, index) => {
    const imageUrl = URL.createObjectURL(file);
    return (
      <Image
        key={index}
        src={imageUrl}
        imageProps={{ onLoad: () => URL.revokeObjectURL(imageUrl) }}
      />
    );
  });

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
        <div>
          <div className="flex flex-wrap items-center justify-center">
            <a href="/" className="flex items-center">
              Back to Home
            </a>
            <h2
              style={{
                margin: rem(30),
              }}
            >
              Upload the Steganographic Image
            </h2>
          </div>
        </div>
        <div
          style={{
            width: "60%",
            display: "flex",
            justifyContent: "space-around",
            padding: rem(10),
          }}
        >
          <Dropzone accept={IMAGE_MIME_TYPE} onDrop={setFiles}>
            <div className="flex flex-col items-center justify-center">
              <h3>Upload Image</h3>
              <p>Drag and drop image here or click to upload</p>
            </div>
          </Dropzone>
          <TextInput
            placeholder="Enter Original Image Signature Received"
            size="xl"
            onChange={(e) => {
                setogSign(e.currentTarget.value);
            }}
            radius="md"
            withAsterisk
          />
          <TextInput
            placeholder="Enter Password Here"
            size="xl"
            onChange={(e) => {
              setPassword(e.currentTarget.value);
            }}
            radius="md"
            withAsterisk
            style={{
              marginBlock: rem(10),
            }}
          />
        </div>
        <button
          onClick={() => {
            invoke("decrypt", {
              path: filePath,
              pass: password,
              imageSign: ogSign,
            })
              .then((res) => {
                console.log(res);
              })
              .catch((err) => {
                console.log(err);
              });
          }}
          className="flex items-center justify-center gap-x-2 py-2 px-4 text-white font-medium bg-gray-800 duration-150 hover:bg-gray-700 active:bg-gray-900 rounded-lg md:inline-flex"
        >
          Submit
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-5 h-5"
          >
            <path
              fillRule="evenodd"
              d="M2 10a.75.75 0 01.75-.75h12.59l-2.1-1.95a.75.75 0 111.02-1.1l3.5 3.25a.75.75 0 010 1.1l-3.5 3.25a.75.75 0 11-1.02-1.1l2.1-1.95H2.75A.75.75 0 012 10z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
      <div className="p-10 flex flex-col items-center justify-center w-screen gap-5">
      <h2 className="text-2xl font-bold">Hidden Text In Image</h2>
        <p className="text-lg font-medium">
          {message.message}
          </p>
        <div className="flex flex-col items-center justify-center w-full">
          <h2 className="text-2xl font-bold">Preview</h2>
          <SimpleGrid cols={4} mt={previews.length > 0 ? "xl" : 0}>
            {previews}
          </SimpleGrid>
        </div>
      </div>
    </div>
  );
}

export default Decrypt;
