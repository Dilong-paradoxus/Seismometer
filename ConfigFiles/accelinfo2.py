# This file contains some helper functions to store personal configuration data and
# keep it from being uploaded to the git repository along with program files

def getseiscoords(): #returns the latitude and longitude of the seismometer
    your_lat = 5
    your_long = 6
    coords = (your_lat,your_long)
    return coords

def getfilepath(): #returns the filepath where csv files are stored
    filepath = r"D:\Nick\Python\Seismometer\Github\Seismometer\AccelerometerData\"
    return filepath

def getCOMnumber(): #returns the serial port ID of the seismometer
    COM_port = '12'
    return COM_port
