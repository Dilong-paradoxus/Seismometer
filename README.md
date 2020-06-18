# Seismometer
Code for recording and processing seismic data from a MEMS accelerometer.
## Theory
Seismic waves passing through the earth create accelerations on objects at the surface. A MEMS accelerometer can act as a "strong-motion" seismometer by measuring these accelerations and reporting them to a computer. With a high enough data rate we can use a fast fourier transform to examine the frequency distribution of these waves and make colorful graphs. 
## Requirements
I have only been able to test on a few computers so here's what does work. Feel free to let me know what does/doesn't work if you try it out!

*Microcontroller: Tested on Teensy 4.0 and Razor IMU w/SAMD21. Arduino UNO could probably run the program but not very fast. 
*Recording: Tested on Windows and Linux laptop with 8GB ram and 2.6GHZ 2-core processor. You could probably get away with a lot less, but the pi zero was not able to run the program at a useable speed. You also need enough storage to archive as much data as you need for processing, so at least a few GB if you keep uncompressed files for a week or so. 
*Data processing: Tested on 16GB RAM desktop with 3.4GHZ 6-core. Went pretty slowly on the aforementioned 8GB laptop. Internet required to get USGS earthquake data

## General instructions
First, upload accelserial_twoway.ino to your Teensy using the arduino IDE and teesnyduino. Then, run setup.py and follow the instructions. When you're ready to collect data, run serialread_twoway. It will write the data to the same folder as itself, and create a new file every 6 hours when the Razor resets. When you want to analyze a file, run accel_readfile using the folder path of your acceleration files and it will output graphs for the estimated time of each earthquake arrival based on your location as specified in the file. plot_quakes is a fast way of looking at what earthquakes happening while you were recording data for all data files in a folder. Accelplot is more advanced plotting tool using Bokeh to make prettier and more accurate graphs.
## Tips
* Use a consistent orientation of your IMU to make data interpretation easier. I point the USB port north with the LED and on/off switch facing up. 
* Choose a quiet place for your IMU. It can detect heavy footsteps from across the room on certain floor materials, so choosing a place away from foot traffic or vibrating machinery will help sort out earthquakes from the noise.
* Compress your data files into a zip archive and unzip when necessary to save space (A future update will do this automatically).
* If you change locations or use a different arduino, feel free to edit accelinfo.py under \ConfigFiles\ 
* Monitor the output file to make sure everything is working correctly. 
