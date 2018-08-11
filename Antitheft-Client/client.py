import os
import time
import threading

import RPi.GPIO as GPIO
import multiprocessing

import cv2
import numpy as np

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import signal
import requests

import json

EMAIL = 'proantitheft@gmail.com'
PASSWORD = 'sciencesciences8307'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# ################ Connection Setup ####################

# bulb = pin 16 ( GPIO 23 )
# siren = pin 18 ( GPIO 24 )
# pir = pin 22 ( GPIO 25 )
# ServoMotor ( Gas ) = pin 32 ( GPIO 12 )
# DistanceSensor = pin 38 ( GPIO 10 ), pin 39 ( GPIO 20 )
# ServoMotor ( door ) = pin 7 ( GPIO 4 )

bulbpin = 23
sirenpin = 24
pirpin = 25
gaspin = 12
doorpin = 4


# ################ End  Connection Setup ####################

# Functions

class TimeoutException(Exception):  # Custom exception class
    pass


def timeout_handler(signum, frame):  # Custom signal handler
    raise TimeoutException


def enablesystem():
    data = None
    with open('settings.json', 'r') as settings_file:
        data = json.load(settings_file)
    if data['enablesystem'] == 'true':
        return True
    return False


def detectmotion():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pirpin, GPIO.IN)

    try:
        time.sleep(0.1)  # to stabilize sensor
        while True:
            if GPIO.input(pirpin):
                print("Motion Detected...")
                return True
            else:
                print('no')
            time.sleep(0.1)  # loop delay, should be less than detection delay

    except:
        GPIO.cleanup()


def gpio_high(pinno):
    pinno = int(pinno)
    print('high=', pinno)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinno, GPIO.OUT)
    GPIO.output(pinno, GPIO.HIGH)


def gpio_low(pinno):
    pinno = int(pinno)
    print('low=', pinno)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinno, GPIO.OUT)
    GPIO.output(pinno, GPIO.LOW)


def mail_to_owners():
    print('mail_to_owners')


def call_to_owners():
    print('called')


def sms_to_owners():
    print('sms')


def verifyface():
    recognizer = cv2.createLBPHFaceRecognizer()
    recognizer.load('recognizer/trainingData.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    found = False
    cam = cv2.VideoCapture(0)
    font = cv2.cv.InitFont(cv2.cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 1, 1)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if (conf < 50):
                if (Id == 101):
                    Id = "PRATEEK"
                    found = True
                    print(Id)
                    break
                elif (Id == 456):
                    Id = "PRASHANT"
                    found = True
                    print(Id)
                    break
            else:
                Id = "Unknown"
            cv2.cv.PutText(cv2.cv.fromarray(im), str(Id), (x, y + h), font, 255)
        if found:
            break
        # cv2.imshow('im',im)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    if found:
        cam.release()
        cv2.destroyAllWindows()
        return True
    else:
        return False


while True:
    print("Started Process...")
    if detectmotion():
        if enablesystem():
            gpio_high(pinno=bulbpin)
            verified = False
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            try:
                verified = verifyface()
            except TimeoutException:
                pass
            else:
                signal.alarm(0)
            if not verified:
                gpio_high(pinno=sirenpin)
                gpio_high(pinno=gaspin)
                gpio_high(pinno=doorpin)
                mail_to_owners()
                call_to_owners()
                sms_to_owners()
                while True:
                    if not enablesystem():
                        gpio_low(pinno=sirenpin)
                        gpio_low(pinno=gaspin)
                        gpio_low(pinno=doorpin)
                        break
                    time.sleep(0.1)
            else:
                gpio_low(pinno=bulbpin)
    time.sleep(1)
