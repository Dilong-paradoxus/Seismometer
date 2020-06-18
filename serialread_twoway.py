#This program communicates with the seismometer and sanely interprets
#data received from the seismometer

#import libraries
import os
import csv
import serial
from time import sleep
from datetime import datetime

#Open serial port
def serialopen():
    if os.name == 'nt': #windows
        portname = 'COM4' 
    else: #linux or whatever
        portname = '/dev/ttyACM0'
        
    print('opening serial port at ' +  portname)
    portopen = [False,0] #initialize variable to hold number of failed tries
    while portopen[0] == False:
        portopen[1] = portopen[1] + 1
        print('try #' + str(portopen[1])) #print number of tries 
        try:    
            seropen = serial.Serial(portname,baudrate=500000) #open serial
            portopen[0] = True #probably unnecessary
            filename = set_filename()
            print('serial success')
            return seropen, filename #return the serial port to be used
        except (PermissionError): #not sure if this actually works
            print('PermissionError')
            sleep(2)
        except (OSError, serial.SerialException): 
            print('OSError or SerialException')
            sleep(2) #wait for the serial device to turn on or be plugged in

def set_filename():
    print(datetime.utcnow())
    filename = 'test.csv'

    timestring = datetime.utcnow().strftime('%Y%m%d_%H%M')
    current_path = os.getcwd()
    filename = str(current_path) + timestring + '_UTC_accel.csv'
    print(filename)
    return filename

def sensor_reset():
    print('reset')
            
def send_time(ser):
    rcvdmsg = [9999]
    timenow = []
    while rcvdmsg != timenow:
    
        print('sending time command')
        timecommand = 'TIM'.encode('utf-8')
        ser.write(timecommand)

        rcvdmsg = split_data(read_serial(ser))
        
    return

def rcv_SEN(sen_data,filename): #parses sensor metadata
    sen_data = split_data(sen_data)
    write_file(sen_data,filename)
    print(sen_data)
    return sen_data

def read_serial(ser): #grabs latest line from serial port
    try:
        ser_bytes = ser.readline() #read one line from serial port
        decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8")) #convert that line to a normal string
        return 1,decoded_bytes,0 #return bit saying data is good, the data, and a zero
    except (OSError, serial.SerialException):
        ser.close() #end serial connection
        print('serial error, retrying')
        sleep(0.5)
        ser,filename = serialopen()
        return 0,ser,filename
    
def write_file(line,filename): #takes line to write and path of file
        with open(filename,"a") as f: #write serial to file
            #writer = csv.writer(f,delimiter=",") #set delimiter as ','
            #writer.writerow(line) #write row
            f.write(str(line) + "\r\n")
            
def split_data(input_data): #move data into a dictionary
    #print("line 86: " + str(input_data))
    input_data = input_data.split(',')
    #print("line 88: " + str(input_data))
    data = {}
    for item in input_data:
        if item != '':
            item = item.split()
            #print("line 93" + str(item))
            data[item[0]] = item[1]
            #print(item[0] + '-' + item[1])
    #print(data)
    return data 

def msg_cases(decoded_bytes,filename,ser):
    msg_code = str(decoded_bytes[0:3])
    print(msg_code)
    print("raw decoded: " + decoded_bytes)

    if msg_code == "DAT": 
        write_file(split_data(decoded_bytes),filename)
        return 0
    elif msg_code == "RES":
        print('resetting')
        return 0
    elif msg_code == "SEN":
        return 'SEN', rcv_SEN(decoded_bytes,filename)
    elif msg_code == "TIM":
        return 'TIM', send_time(ser)
    elif msg_code == "BOOP":
        print('BOOP')
        return 0
    else:
        return 0

    # switcher = {
    #     "DAT": write_file(decoded_bytes,filename),
    #     "SEN": rcv_SEN(decoded_bytes),
    #     "TIM": send_time(ser),
    #     "BOOP": print('BOOP')
    # }
    # x = switcher.get(str(decoded_bytes[0:3]),0)
    # return x
         
starttime = datetime.utcnow() #set starttime to current time
ser, filename = serialopen() #open serial port
ser.reset_input_buffer() #clear buffer of any previous data

metadata = 0
ser.write('SEN'.encode('utf-8'))
#ser.write('DAT'.encode('utf-8'))

while True:
    #ser.write('DAT'.encode('utf-8')) #request data
    ser_bit, ser_data, fname = read_serial(ser) 

    if ser_bit == 0: #if read_serial returns error
        ser = ser_data #set ser to whatever read_serial returned
        filename = fname #set the filename to whatever read_serial returned
        if metadata != 0:
            write_file(metadata,filename)
        else: 
            ser.write('SEN'.encode('utf-8'))
        continue #restart loop

    msg_cases_return = msg_cases(ser_data,filename,ser)
    print(str(msg_cases_return))
    if msg_cases_return != 0:
        if msg_cases_return[0] == 'SEN':
            metadata = msg_cases_return[1]
        elif msg_cases_return[0] == 'TIM':
            print('time received')
            print(msg_cases_return[1])
    

ser.close()

#print(line + timeleftstring) #print serial to terminal
