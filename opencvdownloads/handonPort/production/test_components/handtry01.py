import cv2
import mediapipe as mp
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import uuid
import os

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


sfilepath = "/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/64stringimg.txt"

save_folder = '/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/cropped_hands'
os.makedirs(save_folder, exist_ok=True)



cap = cv2.VideoCapture(0)


def breakdownimg(image_in):
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

        
        if results.multi_hand_landmarks:
            # for num, hand in enumerate(results.multi_hand_landmarks):
            #     mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
            #                             mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=5, circle_radius=7),
            #                             mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=5, circle_radius=5),
            #                             )

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
            file_name = os.path.join(save_folder, f'cropped_hand_test.jpg')
            cv2.imwrite(file_name, cropped_hand)



os.makedirs(save_folder, exist_ok=True)
file_count = 0
with open(sfilepath,"w") as sfile:
    cap = cv2.VideoCapture(0)
    file_count = 0
    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands: 
        while cap.isOpened():
            ret, frame = cap.read()
            

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            image = cv2.flip(image, 1)
            
            image.flags.writeable = False
            
            results = hands.process(image)
            
            image.flags.writeable = True
            
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            x_min = y_min = float('inf')
            x_max = y_max = 0
            cropped_hand = 0

            
            if results.multi_hand_landmarks:
                for num, hand in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=5, circle_radius=7),
                                            mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=5, circle_radius=5),
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

                    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)


                    cropped_hand = image[y_min:y_max, x_min:x_max]
                    key = cv2.waitKey(10)
                    if key == ord('s'):
                        try:
                            file_name = os.path.join(save_folder, f'cropped_hand_{file_count}.jpg')
                            file_count+=1
                            cv2.imwrite(file_name, cropped_hand)
                            print(f"Saved cropped hand as: {file_name}")


                            #Converting to 64 BYTE IMAGE
                            pil_image = Image.fromarray(cv2.cvtColor(cropped_hand, cv2.COLOR_BGR2RGB))
                            buffered = BytesIO()
                            pil_image.save(buffered, format="JPEG")
                            base64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            sfile.write(str(base64_string)+"\n")
                            print("Cropped hand as base64:", " exists")
                        except:
                            print("unable to write")
                
            
            cv2.imshow('Hand Tracking', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

cap.release()

sfile.close()
cv2.destroyAllWindows()
