#This walks the user through the process of setting up their accelinfo.py

import os

print("Welcome! This will generate a new accelinfo.py if you don't already have one.")
print("Checking for accelinfo.py...")

workdir = os.getcwd()
filename = workdir + '\\ConfigFiles\\accelinfo.py'
print('Current location: ' + workdir)

if os.path.isfile(filename) == False:
    print("accelinfo.py doesn't exist yet, creating it now")
    with open(filename,"a") as f: #write serial to file
        f.write('# This file contains some helper functions to store personal configuration data and\n')
        f.write('# keep it from being uploaded to the git repository along with program files\n')
        f.write('\n')

        #Sensor coordinates: getseiscoords()
        f.write('def getseiscoords(): #returns the latitude and longitude of the seismometer\n')

        usr_input = input('Please type the latitude of your sensor here: ')
        f.write('    your_lat = ' + usr_input + '\n')
        usr_input = input('Please type the longitude of your sensor here: ')
        f.write('    your_long = ' + usr_input + '\n')

        f.write('    coords = (your_lat,your_long)\n')
        f.write('    return coords\n')
        f.write('\n')

        #Filepath: getfilepath()
        f.write('def getfilepath(): #returns the filepath where csv files are stored\n')
        f.write('    filepath = r"' + workdir + '\\AccelerometerData\\"\n')
        f.write('    return filepath\r\n')
        f.write('\n')

        #Serial port: getCOMnumber()
        f.write('def getCOMnumber(): #returns the serial port ID of the seismometer\n') 

        usr_input = input(r'The serial port of your sensor looks like \dev\tty\ACM0 on linux or COM4 on windows.' 
            + '\nPlease type it here: ')
        f.write("    COM_port = '"+ usr_input + "'\n")
        f.write("    return COM_port\n")

    print('All done! Feel free to modify this file later if necessary.')
    #filename.close()

elif os.path.isfile(filename) == True:
    print('accelinfo.py already exists!')
    print('If you need to change something, just open it in your favorite text editor.')
    print('If it is broken somehow, delete or move it and rerun this file.')
    print('Have a nice day!')

else:
    print('Something weird happened. Please try again.')