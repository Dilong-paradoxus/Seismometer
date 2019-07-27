# Seismometer
Code for recording and processing seismic data from a MEMS accelerometer.
## Theory
Seismic waves passing through the earth create accelerations on objects at the surface. A MEMS accelerometer can act as a "strong-motion" seismometer by measuring these accelerations and reporting them to a computer. With a high enough data rate we can use a fast fourier transform to examine the frequency distribution of these waves and make colorful graphs. 
## Requirements
I'm currently using the Razor IMU SAMD21 chip + accelerometer on a linux laptop for data recording, and a windows desktop with 16GB of ram for data analysis. The ADXL345 accelerometer code runs on a raspberry pi zero connected via I2C. Internet connection is required for accelread because it connects to the USGS servers for earthquake data. 
