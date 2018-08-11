import os
import time
import threading
from flask import *
import RPi.GPIO as GPIO
import multiprocessing
import cv2
import numpy as np

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import signal


app = Flask(__name__)


@app.route('/isenablesystem')
def isenablethesystem():
    if app.secret_key == request.args.get('secretkey'):
        with open('settings.json', 'r') as settings_file:
            data = json.load(settings_file)
        if data['enablesystem'] == 'true':
            resp = make_response(YES)
        else:
            resp = make_response(NO)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route('/enablesystem')
def enablethesystem():
    if app.secret_key == request.args.get('secretkey'):
        with open('settings.json', 'r') as settings_file:
            data = json.load(settings_file)
        data['enablesystem'] = 'true'
        with open('settings.json', 'w') as settings_file:
            settings_file.write(json.dumps(data))
        resp = make_response(SUCCESS)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route('/disablesystem')
def disablethesystem():
    if app.secret_key == request.args.get('secretkey'):
        with open('settings.json', 'r') as settings_file:
            data = json.load(settings_file)
        data['enablesystem'] = 'false'
        with open('settings.json', 'w') as settings_file:
            settings_file.write(json.dumps(data))
        resp = make_response(SUCCESS)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.before_first_request
def activate_job():
    def run_job():
        while True:
            print("Run recurring task")
            if app.config['enablesystem']:
                if detectmotion():
                    gpio_high(pinno=bulbpin)
                    verified=False
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
                            if not app.config['enablesystem']:
                                gpio_low(pinno=sirenpin)
                                gpio_low(pinno=gaspin)
                                gpio_low(pinno=doorpin)
                                break
                            time.sleep(0.1)
                    else:
                        gpio_low(pinno=bulbpin)
            time.sleep(1)

    threading.Thread(target=run_job).start()


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    app.secret_key = 'VA7e5qS/5SSS5~8DF!kKK{KN5/.@4T'
    app.config['BASE_DIR'] = BASE_DIR
    app.run('0.0.0.0', 3000, True)
