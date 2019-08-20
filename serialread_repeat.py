#This program reads the serial port for a given amount of time, while
#writing that data to a csv file named according to the starting time

from datetime import datetime, timedelta
from time import sleep
import serial
import csv
import os

def serialopen(port):
    print('opening serial port')
    portopen = [False,0]
    while portopen[0] == False:
        portopen[1] = portopen[1] + 1
        print('try #' + str(portopen[1]))
        try:    
            seropen = serial.Serial(port,baudrate=500000)
            portopen[0] = True
            print('serial success')
            return seropen
        except (OSError, serial.SerialException):
            sleep(2)
            

def waitfordata():
    print('waiting for data')
    tcurrent = 0
    try:
        ser_bytes = ser.readline() #read serial
        decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        tcurrent = process_line(decoded_bytes)
        tcurrent = int(tcurrent[3])
        if tcurrent > 20000:
            return tcurrent
        else:
            print('tcurrent (',tcurrent,') < 20k')
            t = 20 - int(tcurrent/1000)
            while t > 0:
                print('...' + str(t))
                t = t - 1
                sleep(1) # wait while arduino starts up 
            return tcurrent
    except:
        print('tcurrent not readable')
        tcurrent = 0
        t = 20
        while t > 0:
            print('...' + str(t))
            t = t - 1
            sleep(1) # wait while arduino starts up
        return tcurrent
    
def process_line(data):
    linelist = data
    if len(linelist) < 56 or len(linelist) > 43:
        line = linelist
    else:
        #print('bad(1)',linelist)
        return
    
    #line = fa.readline()
    line = line.replace('\"','')
    line = line.replace('\n','')
    line = line.split(',')
    #print(line)
    
    #line[0].replace('"','')
    #line[1].strip('"')
    #line[2].strip('"')
    #line[3].strip('"')
    try:
        x = float(line[0])
        y = float(line[1])
        z = float(line[2])
        t = int(line[3])
        print(x,y,z,t)
        return x,y,z,t
    except:
        print('unparseable line')
        return

ser = serialopen('/dev/ttyACM0')
ser.flushInput()

#set maximum run time of program
end_time = datetime.now() + timedelta(days=7)

#set up filename and folder
starttime = datetime.now().strftime('%Y%m%d_%H%M') #time string
filename = str(starttime + '_' + 'accel.csv') #concat to file suffix

#gather data until end_time is reached
while datetime.now() < end_time:
    waitfordata()
    
    with open(filename,"a") as f:  #write metadata line
        metadatatime = datetime.now().timestamp()
        f.write('metadata: PDT' + str(metadatatime) + ', g, ms, Razor IMU, serial \n')
        
    decoded_bytes = [] #set decoded_bytes to empty 
    while decoded_bytes != 'reset': #run until 'reset' is received
        try:
            ser_bytes = ser.readline() #read serial
            decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            print(decoded_bytes) #print serial to terminal
            with open(filename,"a") as f: #write serial to file
                writer = csv.writer(f,delimiter=",")
                writer.writerow([decoded_bytes])
        except (OSError, serial.SerialException):
            ser.close() #end serial connection
            print('serial error, retrying')
            sleep(0.5)
            ser = serialopen('/dev/ttyACM0')
            waitfordata()
            starttime = datetime.now().strftime('%Y%m%d_%H%M') #time string
            filename = str(starttime + '_' + 'accel.csv') #concat to file suffix
            with open(filename,"a") as f:  #write metadata line
                metadatatime = datetime.now().timestamp()
                f.write('metadata: PDT' + str(metadatatime) + ', g, ms, Razor IMU, serial \n')
    
    print('resetting clock')
    
    ser.close() #end serial connection
    ser = serialopen('/dev/ttyACM0')
    
    #reset filename for new file
    starttime = datetime.now().strftime('%Y%m%d_%H%M') #time string
    filename = str(starttime + '_' + 'accel.csv') #concat to file suffix
    
ser.close() #end serial connection
