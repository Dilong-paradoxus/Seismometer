import os
import glob
from datetime import datetime, timedelta
import time
import numpy as np
import json
import geopy.distance
import urllib.request
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

timesave = False

def plotquakes(start,end):
    #download and parse geojson from USGS
    
    def converttime(inputtime,zone,beginorend,timeformat,timesave=None):
        if beginorend == 'begin':
            inputtime = starttime_s - (60*60*24)
        else:    
            inputtime = starttime_s + (60*60*24)
        if zone == 'UTC':
            inputtime = datetime.utcfromtimestamp(inputtime)
        else:
            inputtime = datetime.fromtimestamp(inputtime)
        if timeformat == 'url':
            inputtime = inputtime.strftime("%Y%m%d_%H%M")
        elif timeformat == 'USGS':
            inputtime = inputtime.strftime("%Y-%m-%dT%H:%M:%S")
        else: 
            inputtime = inputtime.strftime("%Y-%m-%d %H:%M:%S")
        return inputtime
      
    urltime_start = []
    urltime_end = []
    urltime = []
    
    urltime_start = converttime(urltime_start,'UTC','begin','USGS')
    urltime_end = converttime(urltime_end,'UTC','end','USGS')
    urltime = converttime(urltime,'local','begin','url')
    titletime = converttime(urltime,'local','begin','title')
    
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
        seiscoords = (47.7477899,-122.526889) #seismometer location
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
    
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(quakeplottime,quakeplotdist,quakeplotmag,c=quakeplotdepth,s=10)
    #s=quakeplotmag makes dots too small and hard to distinguish
    ax.set_ylabel('Distance (km)')
    ax.set_xlabel('Seconds since epoch')
    ax.set_zlabel('Magnitude')
    plt.title(titletime)
    plt.show
    if timesave == True:
        plt.savefig(urltime + 'earthquakemap.png')
    return(quakelist)
    
for file in glob.glob(r"D:\Nick\Python\*.csv"):
    sizefile = os.path.getsize(file)/1000
    starttime_s = os.path.getctime(file)
    endtime_s = (sizefile / 14.9) + starttime_s
    plotquakes(starttime_s,endtime_s,timesave=False)
