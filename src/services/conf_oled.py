#!/usr/bin/env python3

'''
Programa para mostrar o status do Pocket Beagle 
2022/06/29
'''

from board import SCL, SDA
import busio
import adafruit_ssd1306
import netifaces
import time
import uptime

font='/home/debian/src/Oled/font5x8.bin'

i2c = busio.I2C(SCL, SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

display.fill(0)
display.show()
display.rotate(180)

#print('inicio ....')

i=1
while True:
     lista=netifaces.interfaces()
     #print(lista)
     display.fill(0)
     if 'wlan0' not in lista:
          #print('sem wlan0')
          display.text("IP= sem wlan0",1, 1, 1,  font_name=font, size=1)
     else: 
          try: 
               ad=netifaces.ifaddresses('wlan0')
               xx=ad[netifaces.AF_INET]
               #print(xx)
               d=xx[0]
               #print(d)
               ip=d['addr']
               #print(ip)
               display.text("IP="+ip,1, 1, 1,  font_name=font, size=1)
          except: 
               display.text("IP= netifaces ",1, 1, 1,  font_name=font, size=1)

          
     #display.text("CAN= "+str(i),  1,10, 1,  font_name=font, size=1)
     display.text(time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime()),  1,10, 1,  font_name=font, size=1)
     
     display.text("Upt= "+str(round(uptime.uptime()/3600,2)) +" h" ,  1,19, 1,  font_name=font, size=1)
     i=i+1
     display.show()
     time.sleep(3)
