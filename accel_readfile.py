# Reads and analyzes acceleration files
# combines 190819 and 190708 versions of accel_readfile

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
from scipy import interpolate, fft, signal
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
from accelinfo import getseiscoords, getfilepath
#from 190810_accelplot import accelplotter
import numpy as np
from bokeh.plotting import figure, output_file, show 
from bokeh.layouts import gridplot
from bokeh.models import Range1d
from bokeh.io import save

#%%

#select a file

try: 
    accelx,accely,accelz
except NameError: 
    print('Looking for previous data...')
else:
    usedata_input = input('Use last data? [y/n]')

#lastdata = []
#for i in [accelx,accely,accelz]:
    #try:
        #i
    #except NameError:
        #print('Checking data...')
        #lastdata = False
    #else:
        #lastdata = True
        #usedata_input = input('Use last data? [y/n]')
        #break

#print('No file loaded - continuing')    

if input('Use most recent acceleration file? [y/n] ') == 'n':
    def file_selector():
        print('Please select a file:')
        counter = 0
        for file in glob.glob(getfilepath()):
            print(counter,'-',file)
            counter = counter + 1
        filename = glob.glob(getfilepath())[int(input())]
        return filename
    
    filename = file_selector()

else:
    filename = max(glob.iglob(getfilepath()), key=os.path.getctime) #get path of most recent data file
    
print('Using ' + filename)
    
#%%

#Read metadata
    
print('Reading metadata')
with open(filename, newline='\n') as f:
    reader = csv.reader(f)
    metadata = next(reader)

metadatapresent = True

if 'PDT' in metadata[0]: #if timezone is PDT 
    starttime_s = metadata[0].strip('metadata: PDT')
    
elif 'UTC' in metadata[0]: #if timezone is UTC
    starttime_s = metadata[0].strip('metadata: UTC')
    
elif 'metadata' not in metadata[0]:
    #convert filename to starttime
    starttime = os.path.basename(filename)
    starttime = datetime.strptime(starttime.replace('_accel.csv',''),'%Y%m%d_%H%M')
    #starttime = filename[15:27]
    #starttime = starttime_s.replace('_','')
    #yeartime = starttime[0:3]
    #convert datetime object to seconds
    starttime_s = starttime.timestamp()
    metadatapresent = False #set metadatapresent
    
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
    counter = int(counter)
    for item in starttime_s:
        starttime_s[counter] = int(starttime_s[counter])
        counter = counter + 1 
    
    starttime_s = (datetime(starttime_s) - datetime(1970,1,1)).total_seconds()
    
if metadatapresent == True:
    accelunits = metadata[1]
    timeunits = metadata[2]
    sensorname = metadata[3]
    comstandard = metadata[4]
    accelprecision = 'none' #set precision to 'none' if none is specified
    if len(metadata) > 5:
        accelprecision = metadata[5] #precision = number of digits after the decimal
        
else: 
    accelunits = 'g'
    timeunits = 'ms'
    sensorname = 'unknown'
    comstandard = 'serial'
    accelprecision = 'none'
    
#%%
    
print('Reading file:' + filename)

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
    print('Warning: large gap between time measurements:' + str(round(maxdiff,3)) + 's')
    
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

minUSGSmag = '1.5'
maxUSGSmag = '10.0'

urlUSGS = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=' #start of url
urlUSGS = urlUSGS + urltime_start + '&endtime=' + urltime_end + '&minmagnitude=' + minUSGSmag #append times based on above calculations

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
    
#plot earthquake distributions
print('Plotting distribution of earthquakes')

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
#plt.savefig(urltime + 'earthquakemap.png')
#return quakelist

#%%

#plot earthquakes, events, or specified timeframe

        
def plot_all():
    print('Plotting all earthquakes')
    quakecount = len(quakelist)
    quakecounter = 0
    for item in quakelist:
        print('Quake 1/' + quakecount)
        accelplotter(item)
        quakecounter = quakecounter + 1
    return

def plot_quake():
    print('Please select an earthquake:')
    counter = 0
    for item in quakelist:
        print(str(counter) + ' - ' + str(round(item[2])) + 'M ' + item[0])
        counter = counter + 1
    
    print()
    accelplotter(quakelist[int(input())])
    return
    
    
def accelplotter(j):
    #print('Generating spectrogram for earthquake ' + str(quakecounter) + '/' + str(len(quakelist)) + ':')
    #print('    ' + str(round(j[2])) + 'M ' + j[0])
    
    quaketime = j[3]
    quaketime = datetime.utcfromtimestamp(quaketime)
    quaketime = quaketime.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    windowstart = (j[5]) - 60 #start spectrogram 1min before arrival
    windowend = windowstart + 240 #end spectrogram after 4min
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
    
    if len(window_accelx) ==  0 or len(window_accely) == 0 or len(window_accelz) == 0:
        print('Array error: too small ):')
        return
    
    accelxnew = interpolateaccel(window_accelx)
    accelynew = interpolateaccel(window_accely)
    accelznew = interpolateaccel(window_accelz)
    
    timenew = np.linspace(-60000,180000,240000)
    #timelength = int((windowend - windowstart) * 1000) #max(window_time_s)
    #timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength)
    
    windowname = j[0] #set name of window to location of quake
    windowname = windowname.replace(" ", "")  #strip whitespace to make a valid filename
    #windowname = windowname + '_' + j[3] + '_'
    windowfilename = str(round(j[2])) + 'M_' + windowname + '.html' #generate filename
    
    def accelplot(colortheme):
        if colortheme == 'default':
            colortheme = ['white','steelblue','steelblue','steelblue']
        if colortheme == 'tcolor':
            colortheme = ['dimgray','lightskyblue','pink','white']
        
        #set output file name
        output_file(str(round(j[2])) + 'M_' + windowname + '_acceleration.html')
        
        #create three plots
        pwidth = 1800
        pheight = 250
        
        pxaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='x axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pxaccel.line(timenew,accelxnew,legend='x',line_width=1,line_color=colortheme[1])
        pxaccel.x_range=Range1d(-6000,180000)
        
        pyaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='y axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pyaccel.line(timenew,accelynew,legend='y',line_width=1,line_color=colortheme[2])
        pyaccel.x_range=Range1d(-6000,180000)
        
        pzaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='z axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pzaccel.line(timenew,accelznew,legend='z',line_width=1,line_color=colortheme[3])
        pzaccel.x_range=Range1d(-6000,180000)
        
        
        #show(grid)
        return pxaccel,pyaccel,pzaccel
    
    accelgrid = accelplot('default')
    
    #pxaccel,pyaccel,pzaccel = accelgrid 
    pxaccel = accelgrid[0]
    pyaccel = accelgrid[1]
    pzaccel = accelgrid[2]
    #pxaccel = pxaccel[0]
    #return pxaccel
    
    timenew = np.linspace(-60000,180000,240000)
           
    def fftaccel3(axis,axisname):
        sampling_rate = 1000 # Hz
        #N = windowend - windowstart # array size
        N = 240000
        #accelxshort = accelxnew[(start_time*sampling_rate):(end_time*sampling_rate)]

        # Nyquist Sampling Criteria (for interpolated data)
        T = 1/sampling_rate
        xfft = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

        # FFT algorithm
        yr = fft(axis) # "raw" FFT with both + and - frequencies
        yfft = 2/N * np.abs(yr[0:np.int(N/2)]) # positive freqs only
        
        p1=figure(tooltips=[("x", "$x"), ("y", "$y")],y_axis_type='log',
                            plot_width=500,plot_height=500,
                            toolbar_location="left",
                            title=axisname + ' axis fast fourier transform',)
        p1.x_range=Range1d(0,300)
        p1.line(xfft,yfft,)
        #show(p1)
        
        f, t2, Sxx = signal.spectrogram(axis, fs=1000, nperseg = 1000)
        
        p = figure(title=axisname + ' axis spectrogram',
                   tooltips=[("time", "$t2"), ("freq.", "$f"), ("value", "@Sxx")],
                   plot_width=1800,plot_height=250,
                   toolbar_location='left')
        p.x_range.range_padding = p.y_range.range_padding = 0
        
        #original palette: spectral11
        p.image(image=[np.log(Sxx)], x=0, y=0, dw=10, dh=10, palette="Plasma256")
        #mapper = linear_cmap(field_name=Sxx,low=min(Sxx),high=max(Sxx))
        #color_bar = ColorBar(color_mapper=mapper['transform'],width=8,location=(0,0))
        #p.add_layout(color_bar,'right')
        
        output_file(str(round(j[2])) + 'M_' + windowname +
            axisname + '_fft.html')
        
        #show(grid)
        return p1, p
    
       
    fftx = fftaccel3(accelxnew,'x')
    ffty = fftaccel3(accelynew,'y')
    fftz = fftaccel3(accelznew,'z') 
    
    fftxtop = fftx[0]
    fftxspec = fftx[1]
    fftytop = ffty[0]
    fftyspec = ffty[1]
    fftztop = fftz[0]
    fftzspec = fftz[1]
    
    gridx = gridplot([pxaccel,fftxspec],ncols=1)
    smallgridx = gridplot([fftxtop,gridx],ncols=2)
    
    gridy = gridplot([pyaccel,fftyspec],ncols=1)
    smallgridy = gridplot([fftytop,gridy],ncols=2)
    
    gridz = gridplot([pzaccel,fftzspec],ncols=1)
    smallgridz = gridplot([fftztop,gridz],ncols=2)
    
    
    biggrid = gridplot([smallgridx,smallgridy,smallgridz],ncols=1)
    output_file(windowfilename)
    save(biggrid)
    #show(biggrid)

def plot_range():
    print('hi')
    window_bounds = get_window()
    windowstartinput, windowendinput = window_bounds
    windowstart = windowstartinput + starttime_s
    windowend = windowendinput + starttime_s
    print('Window: ' + str(windowstart) + ' to ' + str(windowend))
        
    plottedgraph = plot_window(windowstart,windowend)
    print('Outputting')
    
    windowname = str(windowstartinput) + ' to ' + str(windowendinput) + ' seconds'
    windowfilename = urltime + '_' + str(windowstartinput) + 's_to_' + str(windowendinput) + 's' + '.html'
    output_file(windowfilename)
    
    show(plottedgraph)
    return

def get_window():
    windowstart = starttime_s
    windowend = endtime_s
    windowstartinput = 0
    windowendinput = int(endtime_s - starttime_s)
    print('File length: ' + str(windowendinput) + ' seconds')
    defaultokay = input('Use start and end of file? [y/n] ')
    if defaultokay == 'n':
        print('Available values: 0 to ' + str(int(endtime_s - starttime_s)) + ' seconds')
        print('Tip: plot 240s or less for best performance')
        windowstartinput = int(input('Enter start of window in seconds: '))
        windowendinput = int(input('Enter end of window in seconds: '))
    return windowstartinput,windowendinput

def plot_events():
    print('Plotting all acceleration events')
    
    return

def plot_window(windowstart,windowend):
    
    print('Generating indices')
    windowindices = []
    for kindex, k in enumerate(time_s): #find indices of times in window for 
        if k <= windowstart:
            continue
        if k >= windowend:
            continue
            #print(windowend)
        windowindices.append(kindex)
    
    print('Cutting arrays')
    window_accelx = accelx[windowindices] #cut down arrays to times in the window
    window_accely = accely[windowindices]
    window_accelz = accelz[windowindices]
    window_time_s = []
    for row in windowindices:
        window_time_s.append(time_s[row])
    
    print('Interpolating data')
    def interpolateaccel(axis):
        f = interpolate.interp1d(window_time_s,axis,kind='cubic') #make interpolation function
        timelength = int((windowend - windowstart) * 1000) #max(window_time_s)
        timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength) #generate even time values
        accelaxisnew = f(timenew) #actually use interpolation function
        return accelaxisnew
    
    if len(window_accelx) ==  0 or len(window_accely) == 0 or len(window_accelz) == 0:
        print('Array error: too small ):')
        return
    
    accelxnew = interpolateaccel(window_accelx)
    accelynew = interpolateaccel(window_accely)
    accelznew = interpolateaccel(window_accelz)
    
    timelength = int((windowend - windowstart) * 1000) #max(window_time_s)
    timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength)
    
    #windowname = str(windowstartinput) + ' to ' + str(windowendinput) + ' seconds'
    #windowfilename = urltime + '_' + str(windowstartinput) + 's_to_' + str(windowendinput) + 's' + '.html'
    
    print('generating acceleration plots')
    def accelplot(colortheme):
        if colortheme == 'default':
            colortheme = ['white','steelblue','steelblue','steelblue']
        if colortheme == 'tcolor':
            colortheme = ['dimgray','lightskyblue','pink','white']
        
        
        #create three plots
        pwidth = 1800
        pheight = 250
        
        pxaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='x axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pxaccel.line(timenew,accelxnew,legend='x',line_width=1,line_color=colortheme[1])
        pxaccel.y_range=Range1d(-0.5,0.5) #sets 
        pxaccel.x_range.range_padding = 0 #lines up graph w/fft graph 
        
        pyaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='y axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pyaccel.line(timenew,accelynew,legend='y',line_width=1,line_color=colortheme[2])
        pyaccel.y_range=Range1d(-0.5,0.5)
        #pyaccel.y_range=pxaccel.y_range #links multiple graphs
        pyaccel.x_range.range_padding = 0 #lines up graph w/fft graph
        
        pzaccel = figure(plot_width=pwidth,plot_height=pheight,
                    title='z axis acceleration',
                    background_fill_color=colortheme[0],
                    toolbar_location=None,
                    tooltips=[("x", "$x"), ("y", "$y")])
        pzaccel.line(timenew,accelznew,legend='z',line_width=1,line_color=colortheme[3])
        pzaccel.y_range=Range1d(-1.5,-0.5)
        pzaccel.x_range.range_padding = 0 #lines up graph w/fft graph
        
        return pxaccel,pyaccel,pzaccel
    
    accelgrid = accelplot('default')
    
    #pxaccel,pyaccel,pzaccel = accelgrid 
    pxaccel = accelgrid[0]
    pyaccel = accelgrid[1]
    pzaccel = accelgrid[2]
    #pxaccel = pxaccel[0]
    #return pxaccel
    
    #timenew = np.linspace(-60000,180000,240000)
    
    print('Generating fast fourier transform plots')       
    def fftaccel3(axis,axisname):
        sampling_rate = 1000 # Hz
        N = (windowend - windowstart) *1000 # array size
        #N = 240000
        #accelxshort = accelxnew[(start_time*sampling_rate):(end_time*sampling_rate)]

        # Nyquist Sampling Criteria (for interpolated data)
        T = 1/sampling_rate
        xfft = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

        # FFT algorithm
        yr = fft(axis) # "raw" FFT with both + and - frequencies
        yfft = 2/N * np.abs(yr[0:np.int(N/2)]) # positive freqs only
        
        p1=figure(tooltips=[("x", "$x"), ("y", "$y")],y_axis_type='log',
                            plot_width=500,plot_height=500,
                            toolbar_location="left",
                            title=axisname + ' axis fast fourier transform',)
        p1.x_range=Range1d(0,300)
        p1.line(xfft,yfft,)
        #show(p1)
        
        f, t2, Sxx = signal.spectrogram(axis, fs=1000, nperseg = 1000)
        
        p = figure(title=axisname + ' axis spectrogram',
                   tooltips=[("time", "$t2"), ("freq.", "$f"), ("value", "@Sxx")],
                   plot_width=1800,plot_height=250,
                   toolbar_location='left')
        p.x_range.range_padding = p.y_range.range_padding = 0
        
        #original palette: spectral11
        p.image(image=[np.log(Sxx)], x=0, y=0, dw=10, dh=10, palette="Plasma256")
        #mapper = linear_cmap(field_name=Sxx,low=min(Sxx),high=max(Sxx))
        #color_bar = ColorBar(color_mapper=mapper['transform'],width=8,location=(0,0))
        #p.add_layout(color_bar,'right')
        
        #output_file(str(round(j[2])) + 'M_' + windowname +
            #axisname + '_fft.html')
        
        #show(grid)
        return p1, p
    
       
    fftx = fftaccel3(accelxnew,'x')
    ffty = fftaccel3(accelynew,'y')
    fftz = fftaccel3(accelznew,'z') 
    
    fftxtop = fftx[0]
    fftxspec = fftx[1]
    fftytop = ffty[0]
    fftyspec = ffty[1]
    fftztop = fftz[0]
    fftzspec = fftz[1]
    
    print('Arranging plots')
    gridx = gridplot([pxaccel,fftxspec],ncols=1)
    smallgridx = gridplot([fftxtop,gridx],ncols=2)
    
    gridy = gridplot([pyaccel,fftyspec],ncols=1)
    smallgridy = gridplot([fftytop,gridy],ncols=2)
    
    gridz = gridplot([pzaccel,fftzspec],ncols=1)
    smallgridz = gridplot([fftztop,gridz],ncols=2)
    
    
    biggrid = gridplot([smallgridx,smallgridy,smallgridz],ncols=1)
    
    
    #output_file(windowfilename)
    #save(biggrid)
    return biggrid
    #show(biggrid)
    
def plot_selector():
    print('Do you want to:')
    print('1 - Plot all earthquakes')
    print('2 - Plot a single earthquake')
    print('3 - Plot all acceleration events')
    print('4 - Plot acceleration for a certain time range')
    print('5 - Exit the program')
    plot_input = input()
    
    if plot_input == '1':
        plot_all()
        
    elif plot_input == '2':
        plot_quake()
        
    elif plot_input == '3':
        plot_events()
        
    elif plot_input == '4':
        plot_range()
        
    elif plot_input == '5':
        print('Exiting')
        return
    
    else:
        print('Invalid number selected, exiting')
        return
    
#Run!
plot_selector()
