import cv2
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
    
detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw = False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])
        
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2
        
        cv2.circle(img, (x1, y1), int(7), (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), int(7), (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), int(7), (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        
        length = math.hypot(x2-x1, y2-y1)
        print(length)
        
        #20 350
        #-65 0
        vol = np.interp(length,[50, 300], [minVol, maxVol])
        #print(vol)
        volume.SetMasterVolumeLevel(vol, None)
        
        
        
        if length < 22:
            cv2.circle(img, (cx, cy), int(7), (0, 255, 255), cv2.FILLED)
            cv2.putText(img, "No Volume", (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
        if length > 300:
            cv2.circle(img, (cx, cy), int(7), (0, 255, 255), cv2.FILLED)
            cv2.putText(img, "Full Volume", (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
            os.system("full.mp3")
        
        
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
        
    cv2.putText(img, str(int(fps)), (10, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0 ,255), 2)
    cv2.imshow("Image", img)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break