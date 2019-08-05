import time
import board
import busio
import adafruit_adxl34x
import datetime

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

#max31855 = adafruit_max31855.MAX31855(spi, cs)

accel = adafruit_adxl34x.ADXL345(i2c)

#setup
#accel.enable_motion_detection()
#accel.data_rate(RATE_3200_HZ)
#DataRate.RATE_200_HZ()
#accel.

#axes = accel.getAxes(True)
#x = axes['x']
#y = axes['y']
#z = axes['z']

#print(x)
#print(y)
#print(z)

starttime = datetime.datetime.now()

while True:
    val = "%f %f %f"%accel.acceleration
    nowtime = datetime.datetime.now()
    ms = str((nowtime-starttime).total_seconds()*1000)
    print(str(val) + ', ' + ms)


