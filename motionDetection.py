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

# Cloudinary credentials
cloud_name = "[YOUR_CREDS]"
api_key = "[YOUR_CREDS]"
api_secret = "[YOUR_CREDS]"

alarm = False
alarm_mode = False
alarm_counter = 0

def getInitialFrame(cap):
    _, start_frame = cap.read()
    start_frame = imutils.resize(start_frame, width=500)
    start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
    start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

    return start_frame

def setCamera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    return cap

cap = setCamera()
start_frame = getInitialFrame(cap)

def initializeGlobals():
    pass

def sendMessageToWhatsapp(image_url, title):
    twilio = TwilioClient(account_sid, token)
    twilio.sendImage(image_url=image_url, to_number="+557999818770", title=title)

def uploadImageToCloud(image_path, title):
    cloud = CloudinaryUploader(cloud_name, api_key, api_secret)
    url = cloud.upload(image_path, title)
    return url

def calculateImageDifference(actual_frame, start_frame):
    frame_bw = cv2.cvtColor(actual_frame, cv2.COLOR_BGR2GRAY)
    frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)
    diff = cv2.absdiff(frame_bw, start_frame)
    
    return diff, frame_bw

def getTime():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def triggerAlarm(frame):
    global alarm
    
    if alarm_mode:
        print(f"ALARM")

        time = getTime()
        filename = f"{time}.jpg"

        cv2.imwrite(filename, frame)

        image_url = uploadImageToCloud(filename, time)
        sendMessageToWhatsapp(image_url, filename)

        os.remove(filename)

    alarm = False

while True:
    _, frame = cap.read()
    frame = imutils.resize(frame, width=500)

    if alarm_mode:
        
        diff, frame_bw = calculateImageDifference(frame, start_frame)
        threshold = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        if threshold.sum() > 250000:
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1

        cv2.imshow("Cam", threshold)

    else:
        cv2.imshow("Cam", frame)

    if alarm_counter > 15:
        if not alarm:
            alarm = True
            alarm_counter = 0
            t = threading.Thread(target=triggerAlarm(frame))
            t.start()

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord('t'):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    
    if key_pressed == ord('q'):
        alarm_mode = False
        break

cap.release()
cv2.destroyAllWindows()
"""
if __name__ == '__main__':
    initializeGlobals()
    main()
"""