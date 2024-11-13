import cv2
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import flask 

model = tf.keras.models.load_model('ASL_model.h5')

class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
               'u', 'v', 'w', 'x', 'y', 'z']


test_folder_location = r"C:\Users\bkarr\OneDrive\Desktop\Projects\aslToEnglish\workingDir\test"
#temp
test_character = "b"
test_path = os.path.join(test_folder_location, test_character)

#Each image will have an array of 36. Whatever is the highest value in that sub-array will be the predicted letter/number for that image. 
for image in os.listdir(test_path):
    file_path = os.path.join(test_path, image) 
    print(file_path)
    
    #Load the image using OpenCV
    image = cv2.imread(file_path)
     
    #Image preprocessing
    input_size = (200, 200)
    image_resized = cv2.resize(image, input_size)
    image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
    image_normalized = image_rgb / 255.0
    image_batch = np.expand_dims(image_normalized, axis=0)

    #Prediction 
    prediction = model.predict(image_batch)

    #Plotting
    plt.grid(False)
    plt.imshow(image_normalized, cmap=plt.cm.binary)
    plt.xlabel("Actual: " + test_character)
    #Finds the largest value out of an array of 36 (0-9 + a-z) and gets the index. 
    #For example if largest value is at index 10 then this will print the letter 'a'
    plt.title("Prediction: " + class_names[np.argmax(prediction)]) 
    plt.show()
