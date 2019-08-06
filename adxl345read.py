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
DataRate = adafruit_adxl34x.DataRate()
DataRate.RATE_800_HZ
print(accel.data_rate)

Range = adafruit_adxl34x.Range()
#print(accel.range)
Range.RANGE_2_G
#print(accel.range)

#set endtime for script
end_time = datetime.now() + timedelta(hours=12)
 
#set filename based on start time
starttime_file = datetime.now().strftime('%Y%m%d_%H%M') #time string
filename = str(starttime_file + '_accel.csv') #concat to file suffix
with open(filename,"a") as f:  #write metadata line
    starttime = datetime.now()
    metadatatime = starttime.timestamp()
    f.write('metadata: PDT' + str(metadatatime) + ', m/s, ms, adxl345, i2c, 6 \n')

while datetime.now() < end_time: #run until specified timedelta
    val = "%f, %f, %f"%accel.acceleration #get acceleration values
    nowtime = datetime.now() #get current time
    ms = str(round((nowtime-starttime).total_seconds()*1000)) #convert to ms
    row = str(val) + ', ' + ms 
    print(row) #print to console
    with open(filename,"a") as f: #write to file
        f.write(row + '\n')
