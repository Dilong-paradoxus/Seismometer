#file reading portion of 190621_accel_combined only

import os
import glob
from datetime import datetime, timedelta
import time
import csv
import numpy as np
import statistics
import json
import geopy.distance
import urllib.request
from scipy import interpolate
from scipy import fft
from scipy import signal
import matplotlib.pyplot as plt
import math
import concurrent.futures

filename = max(glob.iglob(r"D:\Nick\Python\*.csv"), key=os.path.getctime) #get path of most recent data file
#filename = 
#starttime_s = os.path.getctime(filename)
starttime_s = os.path.getmtime(filename)

print('Reading file')
    
with open(filename) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    accelx = []
    accely = []
    accelz = []
    timems = []
    fullrow = []
    skippedtotal = 0
    skippedrowlen = 0
    skippedsplit = 0
    skippedaxis = 0 
    skippedt = 0
    lengthaccellow = 13
    lengthaccelhigh = 15


    for row in readCSV: #step through rows in file
        fullrow = row[0]
        if len(row[0]) < 43: #if row is too short, skip
            #print(len(fullrow))
            skippedtotal = skippedtotal + 1
            skippedrowlen = skippedrowlen + 1
            #print(fullrow)
            continue
        if len(row[0]) > 56: #if row is too long, skip
            skippedtotal = skippedtotal + 1
            skippedrowlen = skippedrowlen + 1
            #print(fullrow)
            #print(len(fullrow))
            continue
        
        fullrow = row[0].split(',') #split row into sections at commas
        #print(fullrow)
        if len(fullrow) != 4: #if wrong number of commas, skip
            skippedtotal = skippedtotal + 1
            skippedsplit = skippedsplit + 1
            #print(fullrow)
            continue
            #print(fullrow) #print whole row
        
        x = fullrow[0]
        x = str(float(x))
        if (len(x) < lengthaccellow) and (len(x) > lengthaccelhigh):
            skippedtotal = skippedtotal + 1
            skippedaxis = skippedaxis + 1
            #print(fullrow)
            continue
        
        y = fullrow[1]
        y = str(float(y))
        if (len(y) < lengthaccellow) and (len(y) > lengthaccelhigh):
            skippedtotal = skippedtotal + 1
            skippedaxis = skippedaxis + 1
            #print(fullrow)
            continue
        
        z = fullrow[2]
        z = str(float(z))
        if (len(z) < lengthaccellow) and (len(z) > lengthaccelhigh):
            skippedtotal = skippedtotal + 1
            skippedaxis = skippedaxis + 1
            #print(fullrow)
            continue
        #print('here')
        t = fullrow[3]
        t.strip()
        if (len(t) > 9) or (len(t) < 1):
            skippedtotal = skippedtotal + 1
            skippedt = skippedt + 1
            #print(fullrow)
            continue
        
        accelx.append(x)
        accely.append(y)
        accelz.append(z)
        timems.append(t)
    
#convert data arrays into stuff matplotlib will accept
print('Converting data arrays')

accelx = np.array(accelx)
accelx = accelx.astype(np.float)

accely = np.array(accely)
accely = accely.astype(np.float)

accelz = np.array(accelz)
accelz = accelz.astype(np.float)

timems = np.array(timems)
timems = timems.astype(np.float)

#convert timems to time_s
print('Converting ms to S')

starttime_s = np.array(starttime_s)
starttime_s = starttime_s.astype(np.float)
time_s = [] #initialize arry
#time_s = [((x/1000)+starttime_s) for x in timems] #time_s = timems converted to s and added to the start time
#endtime_s = time_s[-1] #get end time by reading last value in time_s

def converttoseconds(stamp):
    newstamp = ((stamp/1000)+starttime_s)
    return newstamp

def main():
    #concurrently convert timems to time_s
    with concurrent.futures.ProcessPoolExecutor() as executor:
        time_s = executor.map(converttoseconds, timems)
        return time_s

if __name__ == '__main__':
    main()
    
endtime_s = time_s[-1] #get end time by reading last value in time_s

#calculate statistics
print('Calculating statistics')

timediff = np.diff(time_s)
#meandiff = statistics.mean(timediff)
meddiff = statistics.median(timediff)
#mindiff = min(timediff)
maxdiff = max(timediff)
#devdiff = statistics.stdev(timediff)

if maxdiff > (2 * meddiff): #if difference between max and median is too big
    print('Warning: large gap between time measurements')

#%%
#download and parse geojson from USGS

urltime_start = starttime_s - (60*60*24) #subtract one day to make sure to request the correct time intervals
urltime_start = datetime.utcfromtimestamp(urltime_start)
urltime_start = urltime_start.strftime("%Y-%m-%dT%H:%M:%S") #convert date to YYYY-MM-DDTHH:MM:SS (2019-06-23T01:52:21) for USGS site

urltime_end = starttime_s + (60*60*24) #same as above but add one day
urltime_end = datetime.utcfromtimestamp(urltime_end)
urltime_end = urltime_end.strftime("%Y-%m-%dT%H:%M:%S")

#request url format    
#https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2014-01-01&endtime=2014-01-02&minmagnitude=1.5
print('Getting data from USGS')

urlUSGS = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=' #start of url
urlUSGS = urlUSGS + urltime_start + '&endtime=' + urltime_end + '&minmagnitude=1.5' #append times based on above calculations

#open from url
#format: two digit mag_length of time.geojson
#with urllib.request.urlopen("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week.geojson") as url:
    #data = json.loads(url.read().decode()) #read geojson file

with urllib.request.urlopen(urlUSGS) as url: 
     data = json.loads(url.read().decode()) #read geojson file


#parse features in data
print('Reformatting USGS data')
quakelist = []
quakeplottime = []
quakeplotdist = []
quakeplotmag = []
detectablequakedist = []
detectablequaketime = []
for feature in data['features']:
    i = []
    i.append(feature['properties']['place']) #place name
    i.append(feature['geometry']['coordinates']) #coordinates on earth
    seismag = feature['properties']['mag']
    i.append(seismag) #moment magnitude
    
    seistime = (feature['properties']['time'])/1000
    i.append(seistime) #earthquake initiation time 
        
    earthquakecoords = feature['geometry']['coordinates'] 
    earthquakecoords = [earthquakecoords[1],earthquakecoords[0]] #remove depth
    seiscoords = (47.7477899,-122.526889) #seismometer location
    seisdist = round(geopy.distance.geodesic(earthquakecoords, seiscoords).km)
    i.append(seisdist) #distance between earthquake and seismometer, rounded to nearest km
    seisdeltat = abs((seisdist/2)-60) #time difference between earthquake and expected arrival
    if (seistime + seisdeltat) > endtime_s:
        continue #if earthquake is expected to arrive after end of recording
    if (seistime + seisdeltat) < starttime_s:
        continue #if earthquake is expected to arrive before beginning of recording
    i.append(seisdeltat+seistime) #earthquake arrival time relative to start of program (i.e. referenced to timems)
    
    if 8 * math.exp((0.535 * seismag)) > seisdist:
        detectablequakedist.append(seisdist)
        detectablequaketime.append(seistime)

    quakelist.append(i) #append above to list of earthquakes in machine-readable form
    
    quakeplottime.append(seistime)
    quakeplotdist.append(seisdist)
    quakeplotmag.append(seismag)

plt.figure(1)    
plt.scatter(quakeplottime,quakeplotdist,c=quakeplotmag)
plt.title('Earthquake Distances')
plt.ylabel('Distance (km)')
plt.xlabel('Time (s)')
#plt.savefig('quakedistances.png')
plt.show

xxx = np.linspace(1,9,100)
yyy = []
for row in xxx:
    yyy.append(2 * math.exp(2 * row))

plt.figure(3)
plt.scatter(quakeplotmag,quakeplotdist,c=quakeplotmag)
plt.plot(xxx,yyy)
plt.ylabel('Distance (km)')
plt.xlabel('Magnitude')
plt.ylim(0,2000)
plt.show

#%%
def makequakegraphs(currentquake):
    quaketime = currentquake[3]
    quaketime = datetime.utcfromtimestamp(quaketime)
    quaketime = quaketime.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    windowstart = (currentquake[5]) - 6 #start spectrogram 1min before arrival
    windowend = windowstart + 24 #end spectrogram after 4ming
    if windowstart < starttime_s:
        windowstart = starttime_s #if window starts before data, cut window to data
    if windowend > endtime_s:
        windowend = endtime_s #if window ends before data, cut window to data
    
    windowindices = []
    for kindex, k in enumerate(time_s): #find indices of times in window for 
        if k <= windowstart:
            continue
        if k >= windowend:
            continue
            #print(windowend)
        windowindices.append(kindex)
    
    #windowindices = []
    #windowindicestop = np.where(time_s[time_s >= windowstart])
    #windowindicesbot = np.where(time_s[time_s <= windowend])
    #windowindices = set(windowindicesbot[0]) & set(windowindicestop[0])
    #print(windowindices)
    
    #for k in time_s:
        #windowindices = np.where((k.item() >= windowstart) & (k.item() <= windowend)) #find indices for times in window
        
        #if k <= windowstart:
            #continue
        #if k >= windowend:
            #continue
        #windowindices.append(k)
    
    window_accelx = accelx[windowindices] #cut down arrays to times in the window
    window_accely = accely[windowindices]
    window_accelz = accelz[windowindices]
    window_time_s = []
    for row in windowindices:
        window_time_s.append(time_s[row])
    
    def interpolateaccel(axis):
        f = interpolate.interp1d(window_time_s,axis,kind='cubic') #make interpolation function
        timelength = int((windowend - windowstart) * 1000) #max(window_time_s)
        timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength) #generate even time values
        accelaxisnew = f(timenew) #actually use interpolation function
        return accelaxisnew

    #Traceback (most recent call last):
  #File "190622_accel_readfile.py", line 228, in <module>
    #f = interpolate.interp1d(window_time_s,window_accelx,kind='cubic') #make interpolation function
  #File "/usr/lib/python3/dist-packages/scipy/interpolate/interpolate.py", line 478, in __init__
    #self._spline = splmake(self.x, self._y, order=order)
  #File "/usr/lib/python3/dist-packages/scipy/interpolate/interpolate.py", line 2926, in splmake
    #B = _fitpack._bsplmat(order, xk)
#MemoryError

    f = interpolate.interp1d(window_time_s,window_accelx,kind='cubic') #make interpolation function
    timelength = int((windowend - windowstart) * 1000)
    timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength) #generate even time values
    accelxnew = f(timenew) #actually use interpolation function

    #accelxnew = interpolateaccel(window_accelx)
    accelynew = interpolateaccel(window_accely)
    accelznew = interpolateaccel(window_accelz)
    
    windowname = currentquake[0] #set name of window to location of quake
    windowname = windowname.replace(" ", "")  #strip whitespace to make a valid filename
    windowfilename = windowname + '.png' #generate filename
    
    accelfig = plt.figure(figsize=(12,6))
    def accelplot(axis,axisname,axisnumber): #plot acceleration graphs in a column
        plt.subplot(3,1,axisnumber) 
        plt.plot(timenew,axis)
        plt.title(axisname + ' Acceleration')
        plt.xlabel('Time (ms)')
        plt.ylabel('Acceleration (g)')
        axistop = max(axis)+0.1*max(axis)
        axisbot = min(axis)-0.1*min(axis)
        plt.ylim(axisbot,axistop)
        plt.set_cmap('magma')
        
    accelplot(accelxnew,'x',1) #call accelplot
    accelplot(accelynew,'y',2)
    accelplot(accelznew,'z',3)
    plt.suptitle(str(currentquake[2]) + 'M ' + currentquake[0] + '\n' + quaketime) # main plot title
    plt.tight_layout() #add padding between subplots
    plt.subplots_adjust(top=0.88)
    plt.savefig(str(round(currentquake[2])) + 'M_' + windowname + '_acceleration.png', dpi = 300)
    plt.close('all')    
    
    #compute and plot fft of data in window
    #start_time = 80 # seconds
    #end_time = 90 # seconds
    accelspec = plt.figure(figsize=(8,10))
    def fftaccel(axis,axisname,axisnumber):
        sampling_rate = 1000 # Hz
        N = windowend - windowstart # array size
        #accelxshort = accelxnew[(start_time*sampling_rate):(end_time*sampling_rate)]

        # Nyquist Sampling Criteria (for interpolated data)
        T = 1/sampling_rate
        xfft = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

        # FFT algorithm
        yr = fft(axis) # "raw" FFT with both + and - frequencies
        yfft = 2/N * np.abs(yr[0:np.int(N/2)]) # positive freqs only
        
        # Plotting the results
        plt.subplot(3,2,axisnumber)
        plt.plot(xfft, yfft)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Vibration (g)')
        #plt.xlim(0,20)
        plt.title(axisname + ' Frequency Spectrum')
        #plt.savefig(windowname + '_' + axisname + '_freq.png')

        plt.subplot(3,2,axisnumber+1)
        f, t2, Sxx = signal.spectrogram(axis, 1000, nperseg = 1000)
        plt.pcolormesh(t2, f, np.log(Sxx))
        plt.set_cmap('inferno')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title(axisname + ' Spectrogram')
        plt.ylim(0,20)
        #plt.savefig(windowname + '_' + axisname + '_spec.png')
        
    fftaccel(accelxnew,'x',1)
    fftaccel(accelynew,'y',3)
    fftaccel(accelznew,'z',5)
    plt.suptitle(str(currentquake[2]) + 'M ' + currentquake[0] + '\n' + quaketime) # main plot title
    plt.tight_layout() #add padding between subplots
    plt.subplots_adjust(top=0.88)
    plt.savefig(str(round(currentquake[2])) + 'M_' + windowname + '_spectrogram.png',dpi = 300)
    plt.close('all')
        
def main():
    # Make sure the map and function are working
    print([val for val in map(makequakegraphs, quakelist)])

    # Test to make sure concurrent map is working
    with concurrent.futures.ProcessPoolExecutor() as executor:
        print([val for val in executor.map(makequakegraphs, quakelist)])

if __name__ == '__main__':
    main()