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
from mpl_toolkits.mplot3d import Axes3D
import math
from accelinfo import getseiscoords, getfilepath

#%%

filename = max(glob.iglob(getfilepath()), key=os.path.getctime) #get path of most recent data file 
#starttime_s = os.path.getmtime(filename)
#starttime_s = os.path.getctime(filename)

print('Reading metadata')
with open(filename, newline='\n') as f:
    reader = csv.reader(f)
    metadata = next(reader)
    
if 'PDT' in metadata[0]: #if timezone is PDT 
    starttime_s = metadata[0].strip('metadata: PDT')
    
elif 'UTC' in metadata[0]: #if timezone is UTC
    starttime_s = metadata[0].strip('metadata: UTC')
    
else: #tries to handle messed up time from first files
    starttime_s = metadata[0].strip('metadata: ')
    starttime_s = starttime_s.replace('-',',')
    starttime_s = starttime_s.replace(' ',',')
    starttime_s = starttime_s.replace(':',',')
    starttime_s = list(starttime_s)
    if starttime_s[5] == 0:
        starttime_s[5] = ''
    if starttime_s[8] == 0:
        starttime_s[8] = ''
    starttime_s[19:26] = ''
    starttime_s = ''.join(starttime_s)
    counter = 0
    for item in starttime_s:
        starttime_s[counter] = int(starttime_s[counter])
        counter = counter + 1 
    
    starttime_s = (datetime(starttime_s) - datetime(1970,1,1)).total_seconds()   
    
    #1564828099.0 
    #1564853299.0
    #2019-08-03 10:28:19.272629

accelunits = metadata[1]
timeunits = metadata[2]
sensorname = metadata[3]
comstandard = metadata[4]
accelprecision = 'none' #set precision to 'none' if none is specified
if len(metadata) > 5:
    accelprecision = metadata[5] #precision = number of digits after the decimal

#%%

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
    skippedrows = []
    #lengthaccellow = 13
    #lengthaccelhigh = 15

    if accelprecision == 'none': #if no precision set
        rowlenlow = 43
        rowlenhigh = 56
        lengthaccellow = 13
        lengthaccelhigh = 15
    else: #if precision set, set length limits based on precision
        lengthaccellow = accelprecision + 2
        lengthaccelhigh = accelprecision + 4
        rowlenlow = (lengthaccellow * 3) + 4
        rowlenhigh = (lengthaccelhigh * 3) + 9
    
    for row in readCSV: #step through rows in file
        fullrow = row[0]
        if len(row[0]) < rowlenlow: #if row is too short, skip
            #print(len(fullrow))
            skippedtotal = skippedtotal + 1
            skippedrowlen = skippedrowlen + 1
            #print(fullrow)
            continue
        if len(row[0]) > rowlenhigh: #if row is too long, skip
            skippedtotal = skippedtotal + 1
            skippedrowlen[0] = skippedrowlen + 1
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
time_s = [((x/1000)+starttime_s) for x in timems] #time_s = timems converted to s and added to the start time
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
    print('Warning: large gap between time measurements:' + str(maxdiff) + 's')

#%%
#download and parse geojson from USGS

urltime_start = starttime_s - (60*60*24) #subtract one day to make sure to request the correct time intervals
urltime_start = datetime.utcfromtimestamp(urltime_start)
urltime_start = urltime_start.strftime("%Y-%m-%dT%H:%M:%S") #convert date to YYYY-MM-DDTHH:MM:SS (2019-06-23T01:52:21) for USGS site

urltime_end = starttime_s + (60*60*24) #same as above but add one day
urltime_end = datetime.utcfromtimestamp(urltime_end)
urltime_end = urltime_end.strftime("%Y-%m-%dT%H:%M:%S")

urltime = starttime_s #starttime
urltime = datetime.utcfromtimestamp(urltime)
urltime = urltime.strftime("%Y%m%dT%H%M")

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
quakeplotdepth = []
quakeplotlogdepth = []
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
    quakedepth = earthquakecoords[2]
    earthquakecoords = [earthquakecoords[1],earthquakecoords[0]] #remove depth
    seiscoords = getseiscoords() #seismometer location 
    seisdist = round(geopy.distance.geodesic(earthquakecoords, seiscoords).km)
    if quakedepth > (seisdist / 10): #if depth is large relative to distance of quake
        seisdist = math.sqrt((quakedepth ** 2) + (seisdist ** 2))
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
    quakeplotlogdepth.append(-np.log(abs(quakedepth) + 0.001))
    quakeplotdepth.append(quakedepth)

plt.figure(1)    
plt.scatter(quakeplottime,quakeplotdist,c=quakeplotmag)
plt.title('Earthquake Distances')
plt.ylabel('Distance (km)')
plt.xlabel('Time (s)')
#plt.savefig('quakedistances.png')
plt.show

#cutoffmag = np.linspace(1,9,100)
#cutofftime = np.linspace(quakeplottime[0],quakeplottime[-1],10)
#cutoffdist = np.linspace(0.001,max(quakeplotdist),10)
#cutoffmag = []
#for row in cutofftime:
    #cutoffmag.append(np.log(cutoffdist/2))
#cutoffmag = np.array(cutoffmag)
#for row in cutoffmag:
    #cutoffdist.append(2 * math.exp(2 * row))
    
#cutofftime,cutoffdist = np.meshgrid(cutofftime,cutoffdist)
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(cutofftime,cutoffdist,cutoffmag)


plt.figure(3)
plt.scatter(quakeplotmag,quakeplotdist,c=quakeplotmag)
#plt.plot(xxx,yyy)
plt.ylabel('Distance (km)')
plt.xlabel('Magnitude')
plt.ylim(0,2000)
plt.show

fig = plt.figure()
plt.title('Earthquakes during recording period')
ax = Axes3D(fig)
ax.scatter(quakeplottime,quakeplotdist,quakeplotmag,c=quakeplotdepth,s=10)
#s=quakeplotmag makes dots too small and hard to distinguish
ax.set_ylabel('Distance (km)')
ax.set_xlabel('Seconds since epoch')
ax.set_zlabel('Magnitude')
#ax.scatter(zzz,yyy,xxx)
plt.show
plt.savefig(urltime + 'earthquakemap.png')

#%%
quakecounter = 0
for j in quakelist:
    quakecounter = quakecounter + 1
    print('Generating spectrogram for earthquake ' + str(quakecounter) + '/' + str(len(quakelist)) + ':')
    print('    ' + str(round(j[2])) + 'M ' + j[0])
    
    quaketime = j[3]
    quaketime = datetime.utcfromtimestamp(quaketime)
    quaketime = quaketime.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    windowstart = (j[5]) - 6 #start spectrogram 1min before arrival
    windowend = windowstart + 24 #end spectrogram after 4min
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
    
    windowname = j[0] #set name of window to location of quake
    windowname = windowname.replace(" ", "")  #strip whitespace to make a valid filename
    #windowname = windowname + '_' + j[3] + '_'
    windowfilename = windowname + '.png' #generate filename
    
    accelfig = plt.figure(figsize=(12,6))
    def accelplot(axis,axisname,axisnumber): #plot acceleration graphs in a column
        plt.subplot(3,1,axisnumber) 
        plt.plot(timenew,axis,linewidth=0.5)
        plt.title(axisname + ' Acceleration')
        plt.xlabel('Time (' + timeunits + ')')
        plt.ylabel('Acceleration (' + accelunits + ')')
        axistop = max(axis)+0.2
        #axistop = 2
        axisbot = min(axis)-0.2
        #axisbot = -2
        plt.ylim(axisbot,axistop)
        plt.set_cmap('magma')
        
    accelplot(accelxnew,'x',1) #call accelplot
    accelplot(accelynew,'y',2)
    accelplot(accelznew,'z',3)
    plt.suptitle(str(j[2]) + 'M ' + j[0] + '\n' + quaketime) # main plot title
    plt.tight_layout() #add padding between subplots
    plt.subplots_adjust(top=0.88)
    plt.savefig(str(round(j[2])) + 'M_' + windowname + '_acceleration.png', dpi = 300)
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
    plt.suptitle(str(j[2]) + 'M ' + j[0] + '\n' + quaketime) # main plot title
    plt.tight_layout() #add padding between subplots
    plt.subplots_adjust(top=0.88)
    plt.savefig(str(round(j[2])) + 'M_' + windowname + '_spectrogram.png',dpi = 300)
    plt.close('all')

#%%
    
print('Calculating more statistics')

def find_thresholdvalues(axis):
    shakelist = []
    medianaxis = statistics.median(axis)
    print('calculating')
    stddevaxis = statistics.stdev(axis)
    print('calculating')
    axishigh = medianaxis + (2 * stddevaxis)
    axislow = medianaxis - (2 * stddevaxis)
    print('calculating')
    axishigh = medianaxis + stddevaxis
    axislow = medianaxis - stddevaxis
    
    counter = 0
    for x in axis:
        if x > axishigh or x <axislow:
            shakelist.append(counter) 
        counter = counter + 1
        print(counter)
    return shakelist 
        
threshx = find_thresholdvalues(accelx)
threshx = find_thresholdvalues(accely)
threshx = find_thresholdvalues(accelz)
