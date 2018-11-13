#!/usr/bin/env bash


sudo apt-get install git
sudo apt-get install python-pip
sudo apt-get install python-opencv

sudo pip install -r requirements.txt
sudo pip install requests

cp Antitheft.desktop /home/pi/.config/autostart/Antitheft.desktop
chmod +x startup.py
