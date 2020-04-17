#Libraries
import requests
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import cv2

import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders

import requests
import json

from datetime import datetime


DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
 
id = "tps01"
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
green=21
    
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        i=0
        checked = False
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            if (checked==False):
                i = 0
            if (dist<15):
                print("penuh?... %.1d" % (i+1))
                checked = True
                i = i+1
                if i==5:
                    print("TPSIsFull!")
                    GPIO.setup(green, GPIO.OUT)
                    for i in range(5):
                        GPIO.output(green, GPIO.HIGH)
                    break
            else:
                checked = False
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        
    finally:
        # datetime object containing current date and time
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        else:
            print("Failed to retrieve data from humidity sensor")
        
        print("Get location...")
        send_url = "http://api.ipstack.com/check?access_key=f13cab75b0183cc337a1dd255c4cdc72"
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']
        city = geo_json['city']
        
        API_ENDPOINT = "https://id-smartbin.herokuapp.com/data/tps/"+ id
        
        data = {
            "id_tps" : id,
            "waktu" : timestamp,
            "humidity" : humidity,
            "temp" : temperature,
            "latitude":latitude,
            "longitude":longitude,
            "city":city
        }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers)
        # extracting response text  
        pastebin_url = r.text 
        print("The pastebin URL is:%s"%pastebin_url) 
        
        GPIO.cleanup()