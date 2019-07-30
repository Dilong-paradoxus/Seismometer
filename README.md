# Seismometer
Code for recording and processing seismic data from a MEMS accelerometer.
## Theory
Seismic waves passing through the earth create accelerations on objects at the surface. A MEMS accelerometer can act as a "strong-motion" seismometer by measuring these accelerations and reporting them to a computer. With a high enough data rate we can use a fast fourier transform to examine the frequency distribution of these waves and make colorful graphs. 
## Requirements
I'm currently using the Razor IMU SAMD21 chip + accelerometer on a linux laptop for data recording, and a windows desktop with 16GB of ram for data analysis. The ADXL345 accelerometer code runs on a raspberry pi zero connected via I2C. Internet connection is required for accelread because it connects to the USGS servers for earthquake data. 
## General instructions
First, upload Razor_accelserial to your Razor IMU using the arduino IDE. Then, run serialread_repeat. It will write the data to the same folder as itself, and create a new file every 6 hours when the Razor resets. When you want to analyze a file, run accel_readfile using the folder path of your acceleration files and it will output graphs for the estimated time of each earthquake arrival based on your location as specified in the file. plot_quakes is a fast way of looking at what earthquakes happening while you were recording data for all data files in a folder.  
## Tips
* Use a consistent orientation of your IMU to make data interpretation easier. I point the USB port north with the LED and on/off switch facing up. 
* Choose a quiet place for your IMU. It can detect heavy footsteps from across the room on certain floors, so choosing a place away from foot traffic or vibrating machinery will help sort out earthquakes from the noise.
* Compress your files into a zip archive and unzip when necessary
* both plot_quakes and accel_readfile require a getseiscoords.py file with your location input as (latitude,longitude)
