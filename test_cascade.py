# Importing OpenCV package 
import cv2 
  
# Reading the image 
img = cv2.imread('data/raw_positive_images/ezgif-frame-001.jpg') 
  
# Converting image to grayscale 
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
  
# Loading the required haar-cascade xml classifier file 
haar_cascade = cv2.CascadeClassifier('data/cascades/cascade.xml') 
  
# Applying the face detection method on the grayscale image 
faces_rect = haar_cascade.detectMultiScale(gray_img, 2, 0) 
  
# Iterating through rectangles of detected faces 
for (x, y, w, h) in faces_rect: 
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
  
cv2.imshow('Detected faces', img) 
  
cv2.waitKey(0) 