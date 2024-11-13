from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS module
import cv2
import base64

import mediapipe as mp
from io import BytesIO
from PIL import Image
import numpy as np
import uuid
import os




mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


sfilepath = "/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/64stringimg.txt"
sfile = open(sfilepath,'r')

save_folder = '/Volumes/MinhazHardD/handdetect'
os.makedirs(save_folder, exist_ok=True)

def readimage(s64in):

    base64_string = s64in

    image_data = base64.b64decode(base64_string)
    np_array = np.frombuffer(image_data, np.uint8)
    image_data = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    # image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
    return image_data

def convert_image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    base64_str = base64.b64encode(buffer).decode('utf-8')
    base64_image = f"data:image/png;base64,{base64_str}"
    return base64_image

def remove_background(image):
    return image
    # """Use edge detection to isolate the hand and convert the background to black."""
    # # Convert the image to grayscale
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # # Apply Gaussian Blur to reduce noise and improve edge detection
    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # # Use Canny edge detection to detect edges in the image
    # edges = cv2.Canny(blurred, 50, 150)

    # # Find contours based on the edges
    # contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # # Filter out the largest contour, assuming it's the hand
    # if contours:
    #     largest_contour = max(contours, key=cv2.contourArea)

    #     # Create a mask for the largest contour
    #     hand_mask = np.zeros_like(gray)
    #     cv2.drawContours(hand_mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

    #     # Apply the mask to the original image
    #     filtered_image = cv2.bitwise_and(image, image, mask=hand_mask)

    #     # Set non-hand areas to black
    #     filtered_image[hand_mask == 0] = [0, 0, 0]

    #     return filtered_image
    # else:
    #     print("No hand detected.")
    #     return image


def breakdownimg(image_in,counter):
    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands: 
        frame = image_in
        

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        image = cv2.flip(image, 1)
        
        image.flags.writeable = False
        
        results = hands.process(image)
        
        image.flags.writeable = True
        
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        x_min = y_min = float('inf')
        x_max = y_max = 0
        cropped_hand = 0
        
        image[:] = 255

        
        if results.multi_hand_landmarks:
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(139, 185, 34), thickness=1, circle_radius=0),
                                        mp_drawing.DrawingSpec(color=(18, 243, 17), thickness=2, circle_radius=0),
                                        )

            for hand_landmarks in results.multi_hand_landmarks:

                x_min = y_min = float('inf')
                x_max = y_max = 0
            
                for lm in hand_landmarks.landmark:
                    x, y = int(lm.x * image.shape[1]), int(lm.y * image.shape[0])
                    x_min, y_min = min(x_min, x), min(y_min, y)
                    x_max, y_max = max(x_max, x), max(y_max, y)

                # Draw a rectangle around the hand.
                x_min -= 50
                x_max += 50
                y_min -= 50
                y_max += 50

                # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            cropped_hand = image[y_min:y_max, x_min:x_max]

            # cropped_hand = remove_background(cropped_hand)



            file_name = os.path.join(save_folder, f'cropped_hand_test{counter}.jpg')
            counter+=1
            cv2.imwrite(file_name, cropped_hand)

        image = cv2.flip(image, 1)

        retstring = convert_image_to_base64(image)
        return (retstring)





app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


counter = 0

@app.route("/process-frame", methods=["POST"])
def process_frame():
    global counter
    data = request.json

    # Decode the image from Base64
    image_data = data["image"].split(",")
    imgrec = readimage(str(image_data[1]))
    base64ret = breakdownimg(imgrec,counter)
    counter+=1

    
    return jsonify({"status": "frame processed successfully",
                    "image":base64ret})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
