import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy import interpolate
from scipy import fft
from scipy import signal
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot 
from bokeh.models import ColumnDataSource, LinearColorMapper, Range1d
import statistics
import pandas as pd

#run accel_readfile first to import variables

def accelplot(quakelist,starttime_s,endtime_s,time_s,timeunits,accelunits,accelx,accely,accelz):
    quakecounter = 0
    for j in quakelist:
        quakecounter = quakecounter + 1
        if quakecounter > 2:
            continue
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
    
    
        f = interpolate.interp1d(window_time_s,window_accelx,kind='cubic') #make interpolation function
        timelength = int((windowend - windowstart) * 1000)
        timenew = np.linspace(window_time_s[0],window_time_s[-1],timelength) #generate even time values
        accelxnew = f(timenew) #actually use interpolation function
    
        #accelxnew = interpolateaccel(window_accelx)
        accelynew = interpolateaccel(window_accely)
        accelznew = interpolateaccel(window_accelz)
        
        timenew = np.linspace(-6000,18000,24000)
        
        windowname = j[0] #set name of window to location of quake
        windowname = windowname.replace(" ", "")  #strip whitespace to make a valid filename
        #windowname = windowname + '_' + j[3] + '_'
        windowfilename = windowname + '.png' #generate filename
        
        def accelplot2(axis,axisname,axisnumber):
            output_file(str(round(j[2])) + 'M_' + windowname +
                axisname + '_acceleration.html')
            
            axistop = max(axis)+0.2
            axisbot = min(axis)-0.2
            
            medianaxis = statistics.median(axis)
            stddevaxis = statistics.stdev(axis)
            #axishigh = medianaxis + (2 * stddevaxis)
            #axislow = medianaxis - (2 * stddevaxis)
            axishigh = medianaxis + stddevaxis
            axislow = medianaxis - stddevaxis
        
            p = figure(
                    plot_width=1900, plot_height=900,
                    tools="pan,box_zoom,reset,save",
                    y_range=[axisbot, axistop], 
                    title=(axisname + ' Acceleration'),
                    x_axis_label='Time (' + timeunits + ')',
                    y_axis_label='Acceleration (' + accelunits + ')'
                    )
            
            p.line(timenew, timenew, legend="y=x")
            p.circle(timenew, timenew, legend="time", fill_color="white", size=8)
            p.line(timenew, axis, legend=axisname, line_width=1)
            p.line(timenew,statistics.mean(axis), legend='average value', line_color="red")
            p.line(timenew,axishigh, line_color="orange", legend='1 std deviation')
            p.line(timenew,axislow, line_color="orange")
            
            show(p)
            
            
        def accelplot3():
            #set output file name
            output_file(str(round(j[2])) + 'M_' + windowname + '_acceleration.html')
            
            #create three plots
            p1 = figure(plot_width=1800,plot_height=250,title='x',)
            p1.line(timenew,accelxnew,legend='x',line_width=1)
            
            p2 = figure(plot_width=1800,plot_height=250,title='y',)
            p2.line(timenew,accelynew,legend='y',line_width=1)
            
            p3 = figure(plot_width=1800,plot_height=250,title='z',)
            p3.line(timenew,accelznew,legend='z',line_width=1)
            
            #grid = gridplot([[p1],[p2],[p3]])
            accelgrid = gridplot([p1,p2,p3], ncols=1)
            
            #show(grid)
            return accelgrid
        
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
            
        #accelplot2(accelxnew,'x',1) #call accelplot
        #accelplot2(accelynew,'y',2)
        #accelplot2(accelznew,'z',3)
        accelgrid = accelplot3()
        #plt.suptitle(str(j[2]) + 'M ' + j[0] + '\n' + quaketime) # main plot title
        #plt.tight_layout() #add padding between subplots
        #plt.subplots_adjust(top=0.88)
        #plt.savefig(str(round(j[2])) + 'M_' + windowname + '_acceleration.png', dpi = 300)
        #plt.close('all')    
        
        #compute and plot fft of data in window
        #start_time = 80 # seconds
        #end_time = 90 # seconds
        accelspec = plt.figure(figsize=(8,10))
        def fftaccel(axis,axisname,axisnumber):
            sampling_rate = 1000 # Hz
            N = 24000 # array size
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
            f, t2, Sxx = signal.spectrogram(axis, 1000, nperseg = 1500)
            plt.pcolormesh(t2, f, np.log(Sxx))
            plt.set_cmap('inferno')
            plt.ylabel('Frequency [Hz]')
            plt.xlabel('Time [sec]')
            plt.title(axisname + ' Spectrogram')
            plt.ylim(0,20)
            #plt.savefig(windowname + '_' + axisname + '_spec.png')
            
            return xfft,yfft,yr
            
        def fftaccel2(axis,axisname,axisnumber):
            sampling_rate = 1000 # Hz
            N = 24000 # array size
            #accelxshort = accelxnew[(start_time*sampling_rate):(end_time*sampling_rate)]
    
            # Nyquist Sampling Criteria (for interpolated data)
            T = 1/sampling_rate
            xfft = np.linspace(0.0, 1.0/(2.0*T), int(N/2))
    
            # FFT algorithm
            yr = fft(axis) # "raw" FFT with both + and - frequencies
            yfft = 2/N * np.abs(yr[0:np.int(N/2)]) # positive freqs only
            
            #plotname = 'p' + axisname
            #plotname = figure(plot_width=1800,plot_height=250,title=axisname)
            
            
            
            f, t2, Sxx = signal.spectrogram(axis, 1000, nperseg = 1000)
            i=0
            df_spectogram = pd.DataFrame()
            for freq in range(f.shape[0]):
                for time in range(t2.shape[0]):
                    df_spectogram.loc[i] = [f[freq],t2[time],Sxx[freq][time]]
                    i = i+1
        
            TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
            PALETTE = ['#081d58', '#253494', '#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#edf8b1', '#ffffd9']
            mapper = LinearColorMapper(palette=PALETTE, low=np.min(Sxx), high=np.max(Sxx))
            spectogram_figure = figure(title="Spectogram",x_axis_location="below", plot_width=900, plot_height=400,
                       tools=TOOLS)
            spectogram_figure.background_fill_color = "#eaeaea"
            spectrogram_source = ColumnDataSource(data=dict(Sxx=df_spectogram['Sxx'],Frequency=df_spectogram['Frequency'],Time=df_spectogram['Time']))
            #spectogram_figure.circle(x="Time", y="Frequency", source=spectrogram_source, fill_color={'field': 'Sxx', 'transform': mapper}, line_color=None)
            spectrogram_figure.quad(color=={'field': 'Sxx', 'transform': mapper},source=spectrogram_source,width="Time",height="Frequency")
            spectrogram_figure.grid.visible = False
            
            show(spectrogram_figure)
            
        def fftaccel3(axis,axisname):
            sampling_rate = 1000 # Hz
            #N = windowend - windowstart # array size
            N = 24000
            #accelxshort = accelxnew[(start_time*sampling_rate):(end_time*sampling_rate)]
    
            # Nyquist Sampling Criteria (for interpolated data)
            T = 1/sampling_rate
            xfft = np.linspace(0.0, 1.0/(2.0*T), int(N/2))
    
            # FFT algorithm
            yr = fft(axis) # "raw" FFT with both + and - frequencies
            yfft = 2/N * np.abs(yr[0:np.int(N/2)]) # positive freqs only
            
            p1=figure(tooltips=[("x", "$x"), ("y", "$y")])
            p1.x_range=Range1d(0,200)
            #p.line(timenew,np.real(yr))
            p1.line(xfft,yfft)
            #show(p1)
            
            f, t2, Sxx = signal.spectrogram(axis, fs=1000, nperseg = 1000)
            
            p = figure(tooltips=[("time", "$t2"), ("freq.", "$f"), ("value", "@image")])
            p.x_range.range_padding = p.y_range.range_padding = 0
            
            p.image(image=[np.log(Sxx)], x=0, y=0, dw=10, dh=10, palette="Spectral11")
            
            output_file(str(round(j[2])) + 'M_' + windowname +
                axisname + '_fft.html')
            
            fftgrid = gridplot([p1,p], ncols=2)
            
            #show(grid)
            return fftgrid
            
        def meshgrid_example():
            #import numpy as np

            #from bokeh.plotting import figure, show, output_file
            
            N = 500
            x = np.linspace(0, 10, N)
            y = np.linspace(0, 10, N)
            xx, yy = np.meshgrid(x, y)
            d = np.sin(xx)*np.cos(yy)
            
            p = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
            p.x_range.range_padding = p.y_range.range_padding = 0
            
            # must give a vector of image data for image parameter
            p.image(image=[d], x=0, y=0, dw=10, dh=10, palette="Spectral11")
            
            output_file("image.html", title="image.py example")
            
            show(p)  # open a browser
           
        fftgrid = fftaccel3(accelxnew,'x')    
        fftaccel(accelxnew,'x',1)
        
        l = gridplot([
                [accelgrid],
                [fftgrid]
                ])
        show(l)
        #fftaccel(accelynew,'y',3)
        #fftaccel(accelznew,'z',5)
        #plt.suptitle(str(j[2]) + 'M ' + j[0] + '\n' + quaketime) # main plot title
        #plt.tight_layout() #add padding between subplots
        #plt.subplots_adjust(top=0.88)
        #plt.savefig(str(round(j[2])) + 'M_' + windowname + '_spectrogram.png',dpi = 300)
        #plt.close('all')
        
accelplot(quakelist,starttime_s,endtime_s,time_s,timeunits,accelunits,accelx,accely,accelz)

