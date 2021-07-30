import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import numpy as np
import mediapipe as mp
import time
import HandTrack as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from gtts import gTTS
import os
import imutils

#text to speech
fullVolText = 'Full Volume is set'
noVolText = 'No Volume is set'  
language = 'en'
myobj1 = gTTS(text=fullVolText, lang=language, slow=False)

myobj1.save("full.mp3")
  
#volume setting 
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0

pTime = 0
cTime = 0
    
wCam, hCam = 1080, 720
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
imgBg = cv2.imread("matrix.png")
    
detector = htm.handDetector(detectionCon=0.7)
segmentor = SelfiSegmentation()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = segmentor.removeBG(img, imgBg, threshold = 0.5)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    #red color
    low_red = np.array([0, 120, 70])
    high_red = np.array([10,255,255])
    low_red2 = np.array([170, 120, 70])
    high_red2 = np.array([180, 255,255])
    red_mask1 = cv2.inRange(hsv_img, low_red, high_red)
    red_mask2 = cv2.inRange(hsv_img, low_red2, high_red2)
    red_mask = red_mask1+red_mask2
    red = cv2.bitwise_and(img, img, mask=red_mask)
    #countour of red
    cnts_red = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    cnts_red = imutils.grab_contours(cnts_red)

    #blue color
    low_blue = np.array([70,100,50])
    high_blue = np.array([130,255,255])
    blue_mask = cv2.inRange(hsv_img,low_blue, high_blue)
    blue = cv2.bitwise_and(img, img, mask=blue_mask)
    #countour blue
    cnts_blue = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    cnts_blue = imutils.grab_contours(cnts_blue)

    for c in cnts_red:
        areaRed = cv2.contourArea(c)
        if areaRed>5000:
            cv2.drawContours(img, [c],-1, (0,255,0),3)
            M = cv2.moments(c)
            mcx = int(M["m10"]/M["m00"])
            mcy = int(M["m01"]/M["m00"])
            cv2.circle(img, (mcx, mcy), int(7), (255,255,255), int(-1))
            cv2.putText(img,"Red Pill", (mcx-20,mcy-20), cv2.FONT_HERSHEY_SIMPLEX,2.5,(255,255,255),3)
    
    for c in cnts_blue:
        areaRed = cv2.contourArea(c)
        if areaRed>5000:
            cv2.drawContours(img, [c],-1, (0,255,0),3)
            M = cv2.moments(c)
            mcx = int(M["m10"]/M["m00"])
            mcy = int(M["m01"]/M["m00"])
            cv2.circle(img, (mcx, mcy), int(7), (255,255,255), int(-1))
            cv2.putText(img,"Blue Pill", (mcx-20,mcy-20), cv2.FONT_HERSHEY_SIMPLEX,2.5,(255,255,255),3)
            
            
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw = True)
    if len(lmList) != 0:
        
        # size based filtering 
        area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        print(area)
        if 250 < area < 1000:
            print("yes")
            # find distance between index and thumb
            length, img, lineinfo = detector.findDistance(4, 8, img)
           
            #   20 350
            #  -65  0
            vol = np.interp(length,[50, 300], [minVol, maxVol])
            #print(vol)
            volume.SetMasterVolumeLevel(vol, None)
            
            if length < 22:
                cv2.circle(img, (lineinfo[4], lineinfo[5]), int(7), (0, 255, 255), cv2.FILLED)
                cv2.putText(img, "No Volume", (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
            if length > 300:
                cv2.circle(img, (lineinfo[4], lineinfo[5]), int(7), (0, 255, 255), cv2.FILLED)
                cv2.putText(img, "Full Volume", (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
                os.system("full.mp3")
        
     
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
    cv2.imshow("Image", img)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

