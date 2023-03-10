'''
Modec - Motion Detection System
Coded by: github.com/daviembrito
Version: 0.1
'''

import os
import threading
from datetime import datetime
import cv2
import imutils
from cloudinaryuploader import CloudinaryUploader
from twilioapp import TwilioClient

# Twilio credentials
account_sid = "[YOUR_CREDS]"
token = "[YOUR_CREDS]"
cellphone_number = "[YOUR_CREDS]"
from_number = "[YOUR_CREDS]"

# Cloudinary credentials
cloud_name = "[YOUR_CREDS]"
api_key = "[YOUR_CREDS]"
api_secret = "[YOUR_CREDS]"

# Global variables
alarm = False
alarm_mode = False
max_threshold = 250000
max_alarm_counter = 15

def main():
    global alarm_mode
    cap = setCamera()
    start_frame = getInitialFrame(cap)

    alarm_counter = 0

    while True:
        frame = readNewFrame(cap)

        if alarm_mode:
            
            diff, frame_bw = calculateFrameDifference(frame, start_frame)
            threshold = getThresholdFrame(diff)
            start_frame = frame_bw

            if threshold.sum() > max_threshold:
                alarm_counter += 1
            else:
                if alarm_counter > 0:
                    alarm_counter -= 1

            cv2.imshow("Cam", threshold)

        else:
            cv2.imshow("Cam", frame)

        if alarm_counter > max_alarm_counter:
            if not alarm:
                triggerAlarm(frame)
                alarm_counter = 0

        key_pressed = cv2.waitKey(30)
        if isChangeModeKeyPressed(key_pressed):
            alarm_mode = not alarm_mode
            alarm_counter = 0
        
        if isShutdownKeyPressed(key_pressed):
            alarm_mode = False
            break

    shutdownCamera(cap)

def triggerAlarm(frame):
    global alarm

    alarm = True
    t = threading.Thread(target=sendAlarmFrame(frame))
    t.start()

def sendAlarmFrame(frame):
    global alarm
    alarm = False

    if not alarm_mode:
        return
    
    printDetectionMessage()

    time = getTime()
    filename = writeFrameImage(frame, time)

    image_url = uploadImageToCloud(filename, time)
    sendImageToWhatsapp(image_url, time)

    os.remove(filename)

def writeFrameImage(frame, time):
    filename = f"{time}.jpg"
    cv2.imwrite(filename, frame)

    return filename

def uploadImageToCloud(image_path, title):
    cloud = CloudinaryUploader(cloud_name, api_key, api_secret)
    url = cloud.upload(image_path, title)
    return url

def sendImageToWhatsapp(image_url, title):
    twilio = TwilioClient(account_sid, token, from_number)
    twilio.sendImage(image_url=image_url, to_number=cellphone_number, title=title)

def setCamera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    return cap

def readNewFrame(cap):
    _, frame = cap.read()
    return imutils.resize(frame, width=500)

def getInitialFrame(cap):
    start_frame = readNewFrame(cap)
    start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
    start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

    return start_frame

def calculateFrameDifference(actual_frame, start_frame):
    frame_bw = cv2.cvtColor(actual_frame, cv2.COLOR_BGR2GRAY)
    frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)
    diff = cv2.absdiff(frame_bw, start_frame)
    
    return diff, frame_bw

def getThresholdFrame(diff_frame):
    threshold = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)
    return threshold[1]

def getTime():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def isChangeModeKeyPressed(key):
    return key == ord('c')

def isShutdownKeyPressed(key):
    return key == ord('q')

def printDetectionMessage():
    print(f"[MOVEMENT DETECTED] Sending captured frame")

def shutdownCamera(cap):
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()