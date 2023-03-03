# **Modec**
Movement detection system with WhatsApp image sending and cloud storage

## **About**
The system goal is to provide a movement detector with the additional feature of storing and sending the alert frame captured via Cloudinary and WhatsApp.

Cloudinary API is used to upload a captured image of the moment to the cloud and getting it's URL. After that, Twilio API is used to send the image and it's timestamp to a desired WhatsApp number.

The sensibility of the movement detector can be adjusted by it's threshold and the maximum amount of consecutives alerts. 

## **Installation**

```git clone https://github.com/daviembrito/Modec.git```

## **Usage**

Executing the program:

```python3 modec.py```

Press ```c``` to change to detection mode

Press ```q``` to quit the program
