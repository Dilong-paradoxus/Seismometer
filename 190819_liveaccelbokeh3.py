#run as bokeh serve --show 190819_liveaccelbokeh3.py

from multiprocessing import Process, Queue, Pipe
#from serialread_bokeh import read_serial
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from datetime import datetime, timedelta
from functools import partial
from time import sleep
import serial
import csv
from tornado import gen
from threading import Thread

#create ColumnDataSource to be updated
source = ColumnDataSource(data=dict(x=[], y=[],z=[],t=[]))

#save curdoc to make sure all threads can see it
doc = curdoc()

@gen.coroutine
def update(data):
    linelist = process_line(data)
    
    x = linelist[0]
    y = linelist[1]
    z = linelist[2]
    t = linelist[3]
    
    new_data = dict(x=[x], y=[y],z=[z],t=[t])
    source.stream(new_data, rollover=2500)
    
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
        print('unreadable')
        return
    
def read_serial():
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
                t = 20 - (tcurrent/1000)
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
            
    ser = serialopen('/dev/ttyACM0')
    ser.flushInput()

    #set maximum run time of program
    end_time = datetime.now() + timedelta(days=7)

    #set up filename and folder
    starttime = datetime.now().strftime('%Y%m%d_%H%M') #time string
    filename = str(starttime + '_' + 'accel.csv') #concat to file suffix

    linelist = []
        
    while datetime.now() < end_time:
        waitfordata()
        
        with open(filename,"a") as f:  #write metadata line
            metadatatime = datetime.now().timestamp()
            f.write('metadata: PDT' + str(metadatatime) + ', g, ms, Razor IMU, serial \n')
            
        decoded_bytes = [] #set decoded_bytes to empty 
        counter = 0
        while decoded_bytes != 'reset': #run until 'reset' is received
            counter = counter + 1
            try:
                ser_bytes = ser.readline() #read serial
                decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
                #print(decoded_bytes) #print serial to terminal
                #doc.add_next_tick_callback(partial(update, data=decoded_bytes))
                #sleep(0.1)
                if counter > 10:
                    doc.add_next_tick_callback(partial(update, data=decoded_bytes))
                    counter = 0
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
        
        print('resetting clock')
        
        ser.close() #end serial connection
        ser = serialopen('/dev/ttyACM0')
        
        #reset filename for new file
        starttime = datetime.now().strftime('%Y%m%d_%H%M') #time string
        filename = str(starttime + '_' + 'accel.csv') #concat to file suffix
    
fg = figure(width=1000, plot_height=500, title="Acceleration vs Time",
            x_axis_label='Time',
            y_axis_label='Acceleration (g)',)

fg.line(x='t', y='x',color='red', source=source,legend='x accel')
#fg.circle(x='t', y='x',color='red', source=source,legend='x accel')
fg.line(x='t', y='y', color='blue', source=source,legend='y accel')
#fg.triangle(x='t', y='y', color='blue', source=source,legend='y accel')
fg.line(x='t', y='z',color='green', source=source,legend='z accel')
#fg.square(x='t', y='z',color='green', source=source,legend='z accel')

fg.x_range.follow = "end"
fg.x_range.follow_interval = 2500
fg.x_range.range_padding=0

fg.xgrid.grid_line_color = None
fg.ygrid.grid_line_color = None
fg.background_fill_color = "snow"

doc.add_root(fg)

thread = Thread(target=read_serial)
thread.start()
