import cv2
import mediapipe as mp
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import uuid
import os
import flask


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


sfilepath = "/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/64stringimg.txt"
sfile = open(sfilepath,'r')

save_folder = '/Users/minhazrakin/Desktop/CodeProjects/Hackathons/Github/Hackathon York/opencvdownloads/handonPort/cropped_hands'
os.makedirs(save_folder, exist_ok=True)

def readimage(s64in):

    base64_string = s64in

    print("read")
    image_data = base64.b64decode(base64_string)
    np_array = np.frombuffer(image_data, np.uint8)
    image_data = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    # image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
    file_name = os.path.join(save_folder, f'cropped_hand_test.jpg')
    cv2.imwrite(file_name, image_data)

readimage(sfile.readline())

