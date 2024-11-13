from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS module
import cv2
import base64
import mediapipe as mp
from io import BytesIO
from PIL import Image
import numpy as np
import os
import tensorflow as tf

#Initially Loading Model
model = tf.keras.models.load_model('lineASLClassifier.h5')

predicted_char = None

class_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
               'u', 'v', 'w', 'x', 'y', 'z']


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


sfilepath = "/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/64stringimg.txt"
sfile = open(sfilepath,'r')

save_folder = r"C:\Users\bkarr\Downloads\handdetect"
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

def preprocess_image_for_model(image):
    input_size = (224, 224)
    image_resized = cv2.resize(image, input_size)
    image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
    image_normalized = image_rgb / 255.0  # Normalize to [0, 1]
    image_batch = np.expand_dims(image_normalized, axis=0)  # Add batch dimension
    return image_batch

def predict_character(image):
    processed_image = preprocess_image_for_model(image)
    prediction = model.predict(processed_image)
    predicted_class = class_names[np.argmax(prediction)]
    return predicted_class





def breakdownimg(image_in,counter):
    predicted_char = 'UNKNOWN'
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
        image_orig = np.copy(image)
        
        image[:] = 255

        
        if results.multi_hand_landmarks:
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image_orig, hand, mp_hands.HAND_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=0),
                                        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=0),
                                        )
                

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

                cv2.rectangle(image_orig, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            cropped_hand = image[y_min:y_max, x_min:x_max]

            # cropped_hand = remove_background(cropped_hand)

            predicted_char = predict_character(cropped_hand) 
            # print(predicted_char)   

            # file_name = os.path.join(save_folder, f'cropped_hand_test{counter}.jpg')
            counter+=1
            # cv2.imwrite(file_name, cropped_hand)

        image = cv2.flip(image_orig, 1)
        
        retstring = convert_image_to_base64(image)
        
        return retstring,predicted_char





app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


counter = 0

@app.route("/process-frame", methods=["POST"])
def process_frame():
    global counter
    data = request.json
    #This is the input string in the form of a 64 base string. VERY LONG STRING, I would say not to try printing this out.


    # Decode the image from Base64
    image_data = data["image"].split(",")
    #nothing crazy here we are just splitting the string because the input has something like inputdata, 64BASESTRING
    #so we are spliting it because we want just the 64 base string
    imgrec = readimage(str(image_data[1]))
    #Decoding the image to a actual image jpeg
    #the counter variable is used only to make ordered file names

    #the break down function returns a 64 base string which gets sent back to the front end
    #DO NOT make it return other image types
    #GO INTO the breakdowning function and integrate the tensor flow model
    # I recomend making a function which takes an image (NOT 64BASE STRING) and returns the prediction as a string
    #Then i can just integrate that function back into the breakdowning code
    #Simply you do not really need to touch the existing code
    base64ret,modelpredict = breakdownimg(imgrec,counter)
    counter+=1

    
    return jsonify({"status": "frame processed successfully",
                    "image":base64ret,
                    "prediction":modelpredict})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
