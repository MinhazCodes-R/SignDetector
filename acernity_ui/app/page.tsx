"use client"

import React, { useRef, useState } from "react";
import {CoverDemo} from "../components/cover";
import {TypewriterEffectSmoothDemo} from "../components/typewriter-effect"

export default function App() {
  const streamRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  let sendBoolean = false;

  async function startCamera() {
    try {
      // Check if the camera feed has already been started
      if (!streamRef.current) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }
    } catch (error) {
      console.error("Error accessing the camera:", error);
    }
  }

  function stopCamera() {
    sendBoolean = false;

    if (streamRef.current) {
      // Stop all video tracks
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }

  function printData(){
    console.log(streamRef);
  }

  async function captureAndSendFrame() {
    const videoElement = videoRef.current;

    if (videoElement) {
        // Create a canvas element to capture the frame
        const canvas = document.createElement("canvas");
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        const context = canvas.getContext("2d");
        if (context) {
            // Draw the current video frame on the canvas
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            
            // Convert the canvas to a data URL (Base64-encoded PNG)
            const imageData = canvas.toDataURL("image/png");
            sendToServer(imageData);

        }
    }
  }
  
  async function sendToServer(imgData:any) {
    try {
        const response = await fetch("http://127.0.0.1:3001/process-frame", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: imgData }),
        });
        
        if (!response.ok) {
            throw new Error("Failed to send frame to server");
        }

        const result = await response.json();
        console.log("Server response:", result);
        console.log(imgData);
    } catch (error) {
        console.error("Error sending frame to server:", error);
    }
}

function timerSet(time:number){
  return new Promise((resolve)=>{
    setTimeout(()=>{
      resolve(true);
    },time);
  });
}

async function startSendingToServer(){
  if(sendBoolean){
    console.log(sendBoolean);


    await captureAndSendFrame();
    await timerSet(200);
    startSendingToServer();



  }

  // await captureAndSendFrame();
}




  return (
    <div>
      <CoverDemo></CoverDemo>
      <div className="">
      <h1 className="w-3/12 p-10">Live Camera Feed</h1>
      </div>

      <div className="p-10 rounded-3xl m-5 bg-gradient-to-r from-teal-400 to-blue-500 hover:from-blue-500 hover:to-teal-500">

        <video className="px-10" ref={videoRef} autoPlay playsInline></video>


      </div>

      <button className=" bg-blue-200 rounded-lg p-2 m-10" onClick={()=>{startCamera()}}>Start Camera</button>
      <button className="bg-blue-200 rounded-lg p-2 m-10" onClick={()=>{stopCamera()}}>Stop Camera</button>
      <button className="bg-blue-200 rounded-lg p-2 m-10" onClick={()=>{
        sendBoolean = true;
        startSendingToServer();

      }}>Print Data
      </button>
      <TypewriterEffectSmoothDemo/>

    </div>
  );
}
