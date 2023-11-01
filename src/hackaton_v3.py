#!/bin/python3
#!/usr/bin/env python3
# arquivo /home/debian/src/OBC_GamaGolf/obc_can_gps_mysql.py
#
# Rotina ler dados do GPS e armazenar num banco de dados SQL 
# para seu posterior envio para o ScadaBR via SQL 
# 
# 
# 2021/09/16 Implementacao para MariaDB (MySql)
# 2021/09/19 Implementando servidor ModBusTCP 
#            Usando porta 5020 para garantir o acesso a usuario normal
#            A ModBus manda uma palavra no formato de 2 bytes ou 16 bits
#            falta implementar uma funcao para mandar dados reais  
#            Modificado a rotina do leitura de GPS para nao bloquear 
# 2022/02/16 Mudando para off-line para Jupyter Notebook
#            Testou no GamaGolf e funcionou..!
#            Quando a chave está ligado grava os dados no banco de dados
# 2022/03/19 Mudando para Beagle Bone Black
# 2022/03/19 Corrigindo o painel e acionando diretamente os leds e chaves
# 2022/03/20 Implementando MySqL
# 2022/08/23 Reorganizando o codigo para o Hackaton 2022
#            Os dados sao gravados num único registro a cada segundo baseado no tick 
#            do GPS
#            tabela MariaDB  registro_hackathon
#              create table registro_hackathon (hora timestamp(03), latitude decimal(10,5), longitude decimal(10,5),
#                 velocidade_gps float, altitude float, tensao float, corrente float, velocidade float )
#
# 2022/08/24 Carregando o programa com systemctl e a chave 1 grava os dados no MariaDB na tabela registro_hackathon
# 2022/08/29 corrigindo calibracao da corrente - ainda falta ajustar a altitude
#
# 2023/10/12 Usando um timer thread como base de tempo para gravacao no MariaDB em vez do leitura do GPS.
# 2023/10/13 Corrigido GPS para nao ficar esperando dados
# 2023/10/30 Medindo aceleracao e gyroscopio com MPU6050


import can 
import cantools
import serial
import pynmea2
import time
import datetime

import board 
import adafruit_mpu6050

import threading 

import mysql.connector

from pprint import pprint
from time import sleep
from random import uniform

from pyModbusTCP.server import ModbusServer, DataBank
import netifaces

import signal

import Adafruit_BBIO.GPIO as GPIO

led1 =   "P9_14"
led2 =   "P9_16"
chave1 = "P9_12"
chave2 = "P9_15"

GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(chave1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(chave2, GPIO.IN, GPIO.PUD_UP)

#####   configuracao do serial do GPS 

ser = serial.Serial("/dev/ttyS4",9600, timeout=0.5) # S4

class GPS_nb:    # versao do GPS que nao fica esperando 
	def __init__ (self):
		ser.flushInput()
		ser.flushInput()
	def read(self):
	    if ser.inWaiting()==0 :
	    	self.coordenados=0
	    else :
		    G = ser.readline()
		    self.error=0
		    self.coordenados=0
		    if G != b'' :
			    #self.NMEA = G
			    Gs = G.strip()
			    Gd = Gs.decode(encoding='UTF-8',errors='replace')
			    self.NMEA=Gd
			    Gd_vetor = Gd.split(',')
			    self.code = Gd_vetor[0]
			    if Gd_vetor[0]== '$GPRMC':  # '$GPGGA':
				    #self.coordenados=1
				    try :
					    self.msg = pynmea2.parse(Gd)
					    self.coordenados=1
				    except : self.error = 1


print("Criando GPS na porta serial ")
myGPS=GPS_nb()

print("Abrindo MPU6050 ")

i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c,105)

print("Dados do DBC")
db = cantools.database.load_file('/home/debian/src/DBC/GamaGolfV1.dbc')

print("Abrindo CAN0")
can_bus=can.interface.Bus(bustype='socketcan', channel='can0', bitrate=125000)
print (can_bus.state)
# Falta testar se CAN estiver funcionando...

print("Abrindo MariaDB")
conn = mysql.connector.connect(user='debian', password='sleutel' , host='127.0.0.1', database='trajetorio')
curs = conn.cursor()

print("Abrindo Modbus")
local_IP=netifaces.ifaddresses('wlan0')[2][0]['addr']
server = ModbusServer(local_IP,5020, no_block=True)

#server = ModbusServer("192.168.1.106",5020, no_block=True)
#server = ModbusServer("localhost",5020, no_block=True)
#server = ModbusServer("192.168.15.4",5020, no_block=True)

mb_input_status_chaves=10
mb_input_reg_velocidade=10
mb_input_reg_voltage=11
mb_input_reg_current=12
mb_input_reg_latitude=13
mb_input_reg_longitude=14
mb_input_reg_velocidade_gps=15
mb_input_reg_altitude=16
mb_input_reg_voltage12=17
mb_input_reg_current12=18

mb_input_reg_acelX=20
mb_input_reg_acelY=21
mb_input_reg_acelZ=22
mb_input_reg_gyroX=23
mb_input_reg_gyroY=24
mb_input_reg_gyroZ=25


print("Iniciando server")
try:
    server.start()
    print("Online")
except:
     print("Shutting down")
     server.stop()
     print("Off line")    
    
velocidade=0
voltage=0
current=0
Latitude=0
Longitude=0
Altitude=0
Velocidade_GPS=0

acel_x=0
acel_y=0
acel_z=0
gyro_x=0
gyro_y=0
gyro_z=0

voltage12=1
current12=1

print("Iniciando interrupcao timer 1 seg")

hab_grava_sql = False

# Define temporizacao para gravar o banco com SQL a cada segunda usando thread timer
#create table registro_acelerometro (hora timestamp(03), acel_x float , acel_y float , acel_z float, gyro_x float, gyro_y float, gyro_z float) 


def grava_sql():

    
    tempo_atual=datetime.datetime.now()
    if hab_grava_sql:
            GPIO.output(led1, GPIO.HIGH)
            print("INSERT INTO registro_hackathon (hora, latitude, longitude , velocidade_gps , altitude , tensao, corrente, velocidade) values (%s , %s, %s, %s, %s , %s, %s, %s )",(Hora, Latitude, Longitude, Velocidade_GPS, Altitude, voltage, current, velocidade))
            curs.execute("INSERT INTO registro_hackathon (hora, latitude, longitude , velocidade_gps , altitude , tensao, corrente, velocidade) values (%s , %s, %s, %s, %s , %s, %s, %s )",(Hora, Latitude, Longitude, Velocidade_GPS, Altitude, voltage, current, velocidade))
            print("INSERT INTO registro_acelerometro (hora, acel_x, acel_y, acel_z, gyro_x, gyro_y, gyro_z ) values (%s , %s, %s, %s, %s , %s, %s )",(Hora, acel_x, acel_y, acel_z, gyro_x, gyro_y, gyro_z ))
            curs.execute("INSERT INTO registro_acelerometro (hora, acel_x, acel_y, acel_z, gyro_x, gyro_y, gyro_z ) values (%s , %s, %s, %s, %s , %s, %s )",(Hora, acel_x, acel_y, acel_z, gyro_x, gyro_y, gyro_z ))
            conn.commit()
            GPIO.output(led1, GPIO.LOW)
            
    x=datetime.datetime.now()
    # aqui calcula quanto falta para completar o delay para a proxima chamada de 1hz
    delta=(x-tempo_atual).total_seconds()
    if delta > 1 : 
        print("Erro no temporizacao delta")
        delta=0
    threading.Timer((1-delta),grava_sql).start()
    # Criando thread recursivo
    


# Habilita gravacao no banco de dados a 1hz
grava_sql()


def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        print("Shutting down fim")
        server.stop()
        print("Off line")        
        exit(1)

signal.signal(signal.SIGINT, handler)

# Loop principal para ler os sensores, chaves e atualizar modbus-ip

while True:
    sleep(0.1)  # era 0.001 testando para ver se fica mais leve - caiu de 25% para 3% no top
    pchave1=GPIO.input(chave1)  
    pchave2=GPIO.input(chave2)  
    
    s = str([pchave1, pchave2])
     
    #if pchave1 : GPIO.output(led1, GPIO.HIGH)
    #else : GPIO.output(led1, GPIO.LOW)
    if pchave2 : GPIO.output(led2, GPIO.HIGH)
    else : GPIO.output(led2, GPIO.LOW) 
    
    ## habilitando gravacao no MariaBD
    if pchave1: 
        hab_grava_sql= True
    else:
        hab_grava_sql = False
    
    ## Modbus IP lendo endereco IP atual
    #if pchave2: 
    #        server.stop()
    #        local_IP=netifaces.ifaddresses('wlan0')[2][0]['addr']
    #        server = ModbusServer(local_IP,5020, no_block=True)
    #        server.start()
    
    ## Leia CAN 
    try: 
        mensagem = can_bus.recv(0.0)
    except: 
        print('erro can')
            
    if mensagem is not None :
        mm=db.decode_message(mensagem.arbitration_id, mensagem.data) 
        if mensagem.arbitration_id == db.get_message_by_name('MODINSTRUM').frame_id : 
            if 'Velocity' in mm :
                velocidade=mm["Velocity"]
        if mensagem.arbitration_id == db.get_message_by_name('EVEC2').frame_id : 
            if 'Voltage' in mm :
                voltage=mm["Voltage"]/100
            if 'Current' in mm :
                current=int(mm["Current"]) # /100 # falta fazzer a calibracao aqui
                print (current)
                current=current/100
                if (current > 0x8000) :
                    current = -current
                #current=current/100    
                print (current)    
                
                
        if mensagem.arbitration_id == db.get_message_by_name('BATERIA12V').frame_id :
            if 'Voltage12' in mm :
                voltage12=mm["Voltage12"]/100
            if 'Current12' in mm :
                current12=mm["Current12"]/100

        Hora = datetime.datetime.now()
        s = s  + " , " + str(Hora) + " lendo can = " + str(velocidade) + " km/h, " + str(voltage) + " V, "+ str(current) + " Amp, " + str(voltage12) + " V12, "+ str(current12) + " Amp12. "

    ## Lendo GPS 

    myGPS.read()
    if (myGPS.coordenados == 1) : 
        Latitude =      myGPS.msg.latitude
        Longitude =     myGPS.msg.longitude
        if myGPS.msg.spd_over_grnd == None :
	          Velocidade_GPS = 0 # myGPS.msg.spd_over_grnd
        else : 
              Velocidade_GPS = myGPS.msg.spd_over_grnd
        #Altitude =       myGPS.msg.altitude  ## falta testar
        horario =        myGPS.msg.timestamp   ## falta testar.. !!!
        Hora = datetime.datetime.now()
        s = s + " GPS , " + "%s" % Hora + "  " + "%s" % Latitude + " , " + "%s" % Longitude + " , " +  "%s" % Velocidade_GPS + " , " + "%s" % Altitude

    ## imprime dados lidos dos sensores e chaves
    print(s)
    
    acel_x , acel_y , acel_z = mpu.acceleration
    gyro_x, gyro_y, gyro_z   = mpu.gyro
    

    ## registra dados lidos no modbus
    DataBank.set_bits( mb_input_status_chaves,     [pchave1, pchave2]) 
    
    DataBank.set_words(mb_input_reg_velocidade,    [int(velocidade)])
    DataBank.set_words(mb_input_reg_voltage,       [int(voltage)])
    DataBank.set_words(mb_input_reg_current,       [int(current)])
    DataBank.set_words(mb_input_reg_latitude,      [int(Latitude*100)])
    DataBank.set_words(mb_input_reg_longitude,     [int(Longitude*100)])
    DataBank.set_words(mb_input_reg_velocidade_gps,[int(Velocidade_GPS*100)])
    DataBank.set_words(mb_input_reg_altitude,      [int(Altitude)])
    DataBank.set_words(mb_input_reg_voltage12,     [int(voltage12*100)])
    DataBank.set_words(mb_input_reg_current12,     [int(current12*100)])

    DataBank.set_words(mb_input_reg_acelX, [int(acel_x*100)])
    DataBank.set_words(mb_input_reg_acelY, [int(acel_y*100)]) 
    DataBank.set_words(mb_input_reg_acelZ, [int(acel_z*100)]) 
    DataBank.set_words(mb_input_reg_gyroX, [int(gyro_x*100)]) 
    DataBank.set_words(mb_input_reg_gyroY, [int(gyro_y*100)])
    DataBank.set_words(mb_input_reg_gyroZ, [int(gyro_z*100)]) 
    