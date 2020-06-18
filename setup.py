#This walks the user through the process of setting up their accelinfo.py

import os

print("Welcome! This will generate a new accelinfo.py if you don't already have one.")
print("Checking for accelinfo.py...")

workdir = os.getcwd()
print('Current location: ' + workdir)

if os.path.isfile(workdir + '\\ConfigFiles\\accelinfo.py') == false:
    print('accelinfo.py not found')
    

elif:
    print('accelinfo.py already exists!')
    print('If you need to change something, just open it in your favorite text editor.')
    print('If it is broken somehow, delete or move it and rerun this file.')
    print('Have a nice day!')

else:
    print('Something weird happened. Please try again.')