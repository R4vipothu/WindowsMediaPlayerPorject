from serial.tools import list_ports
import serial
import time
import csv


ports = list_ports.comports()
for port in ports: print(port)

f = open("data.csv", "w", newline='') #open a data file
f.truncate()

serialCom = serial.Serial("COM3", 115200) #connect to the Arduino
print(serialCom)

serialCom.dtr = False
time.sleep(1)
serialCom.reset_input_buffer()
serialCom.dtr = True
#resets the arduino when starting


pointsRecorded = 5 #numPoints recorded
for point in range(pointsRecorded):
    try:
        #read the line
        byte = serialCom.readLine()
        #decode the line
        decodedByte = byte.decode("utf-8")
        print(decodedByte)

    except:
        print("Data point not found")