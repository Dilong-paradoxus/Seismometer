from multiprocessing import Pool
from datetime import datetime
from scipy import interpolate, fft, signal
import numpy as np
from bokeh.plotting import figure, output_file, show 
from bokeh.layouts import gridplot
from bokeh.models import Range1d
from bokeh.io import save

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
    
    accelxnew = interpolateaccel(window_accelx)
    accelynew = interpolateaccel(window_accely)
    accelznew = interpolateaccel(window_accelz)
    
    timenew = np.linspace(-60000,180000,240000)
    
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
        p1.x_range=Range1d(0,200)
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

print('hi')    
for item in quakelist:
    accelplotter(item)

#if __name__ == '__main__':
    #print('hi')
    #with Pool() as pool:
        #pool.map(accelplotter,quakelist)
    