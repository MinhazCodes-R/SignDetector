"use client";

import { div } from "framer-motion/client";
import React, { useRef, useState } from "react";


function WebAccess(){
  const streamRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const videoRef2 = useRef<HTMLVideoElement | null>(null);
  
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  let canvasWidth = 10;
  let canvasHeight = 10;

  const [letter,changeletter] = useState("");


  let sendBoolean = false;



  const drawOnCanvas = (base64in:string) => {
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        // Clear the canvas before drawing
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        const img = new Image();
        img.src = base64in;

        img.onload = ()=>{
          const ratio = img.naturalWidth/img.naturalHeight;

          let height = 250;

          // if (videoRef.current){
          //   height = videoRef.current?.videoHeight;
          // }
          

          canvasRef.current!.height = height;
          canvasRef.current!.width = height*ratio;
          

          // Draw the image onto the canvas
          //fliping the image

        ctx.drawImage(img, 0, 0, height*ratio, height);

        //flipping back

        }
      }
    }
  };
  

  async function startCamera() {
    try {
      // Check if the camera feed has already been started
      if (!streamRef.current) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        if (videoRef2.current){
        }
      }
    } catch (error) {
      console.error("Error accessing the camera:", error);
    }
  }

  function stopCamera() {
    sendBoolean = false;

    setTimeout(() => {
      if (streamRef.current) {
        // Stop all video tracks
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
        

        if (canvasRef.current) {
          const ctx = canvasRef.current.getContext('2d');
          ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        }
      }
      
    }, 100);

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

  let counter = 0;
  let occurange = new Map();
  let mostoccur = ["",0];
  let contained_string = "";
  function renderprediction(prediction:string){


    occurange.has(prediction)?occurange.set(prediction, occurange.get(prediction) + 1):occurange.set(prediction, 1);
    if (occurange.get(prediction) > mostoccur[1]) {
      mostoccur = [prediction, occurange.get(prediction)];
    }

    counter++;
    if (counter === 60) {
      console.log("Most occurring prediction in 30 iterations:", mostoccur[0]);
      if (mostoccur[0] != "UNKNOWN"){
        contained_string += mostoccur[0];
        changeletter(contained_string);
      }

      // Reset counter and occurrence data for the next 30 iterations
      counter = 0;
      mostoccur = ["", 0];
      occurange.clear();
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
        drawOnCanvas(result.image);
        renderprediction(result.prediction);




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



    await captureAndSendFrame();
    await timerSet(30);
    startSendingToServer();

  }
  // await captureAndSendFrame();

}





    return (
        <div className="m-10" style={{zIndex:"100", position:"absolute"}}>
            <div className="">
                </div>

                <div className="flex">

                    <div className="bg-black mx-2 rounded-lg" style={{width:"350px"}}>

                    <video style={{height:"250px"}} className="m-2" ref={videoRef} autoPlay playsInline></video>

                    </div>

                    <div style={{width:"350px"}} className="flex justify-end bg-white mx-2 rounded-lg">

                    <canvas className="p-2" ref={canvasRef}></canvas>

                    </div>
                    <div>
                      <h1 className="text-9xl m-10 text-white">{letter}</h1>
                    </div>


                </div>

                <button className=" bg-blue-200 rounded-lg p-2 mx-5 my-4" onClick={()=>{startCamera()}}>Start Camera</button>
                <button className="bg-blue-200 rounded-lg p-2 mx-5" onClick={()=>{stopCamera()}}>Stop Camera</button>
                <button className="bg-blue-200 rounded-lg p-2 mx-5" onClick={()=>{
                    sendBoolean = true;
                    startSendingToServer();

                }}>Print Data
                </button>

            
        </div>
    );
}

export {WebAccess};