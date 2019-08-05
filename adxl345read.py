import time
import board
import busio
import adafruit_adxl34x
import csv
from datetime import datetime, timedelta

#start i2c communication
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
accel = adafruit_adxl34x.ADXL345(i2c)

#setup accelerometer
#accel.data_rate(RATE_3200_HZ)
#accel.data_rate(RATE_400_HZ)
#accel.range(RANGE_2_G)

#set endtime for script
end_time = datetime.now() + timedelta(hours=12)

#get starttime
starttime = datetime.now()
 
#set filename based on start time
starttime_file = datetime.now().strftime('%Y%m%d_%H%M') #time string
filename = str(starttime_file + '_' + 'accel.csv') #concat to file suffix
with open(filename,"a") as f:  #write metadata line
    f.write('metadata: ' + str( datetime.now) + ' m/s, ms, adxl345, i2c \n')

while datetime.now() < end_time: #run until specified timedelta
#while True: #run forever
    val = "%f00000, %f00000, %f00000"%accel.acceleration #get acceleration values
    nowtime = datetime.now() #get current time
    ms = str(round((nowtime-starttime).total_seconds()*1000)) #convert to ms
    row = str(val) + ', ' + ms 
    print(row) #print to console
    with open(filename,"a") as f: #write to file
        #writer = csv.writer(f,delimiter=",")
        #writer.writerow(row)
        f.write(row + '\n')
