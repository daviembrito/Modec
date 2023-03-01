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

# Global variables
alarm = False
alarm_mode = False
max_threshold = 250000
max_alarm_counter = 15

def main():
    cap = setCamera()
    start_frame = getInitialFrame(cap)

    alarm_counter = 0

    while True:
        frame = readNewFrame(cap)

        if alarm_mode:
            
            diff, frame_bw = calculateImageDifference(frame, start_frame)
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
        if motionKeyIsPressed(key_pressed):
            alarm_mode = not alarm_mode
            alarm_counter = 0
        
        if closeKeyIsPressed(key_pressed):
            alarm_mode = False
            break

    shutdownCamera(cap)

def triggerAlarm(frame):
    global alarm

    alarm = True
    t = threading.Thread(target=sendAlarmFrame(frame))
    t.start()

def readNewFrame(cap):
    _, frame = cap.read()
    return imutils.resize(frame, width=500)

def getInitialFrame(cap):
    start_frame = readNewFrame(cap)
    start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
    start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

    return start_frame

def getThresholdFrame(diff_frame):
    threshold = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)
    return threshold[1]

def setCamera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    return cap

def sendImageToWhatsapp(image_url, title):
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

def sendAlarmFrame(frame):
    global alarm
    
    if alarm_mode:
        print(f"ALARM")

        time = getTime()
        filename = f"{time}.jpg"

        cv2.imwrite(filename, frame)

        image_url = uploadImageToCloud(filename, time)
        sendImageToWhatsapp(image_url, time)

        os.remove(filename)

    alarm = False

def motionKeyIsPressed(key):
    return key == ord('t')

def closeKeyIsPressed(key):
    return key == ord('q')

def shutdownCamera(cap):
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()