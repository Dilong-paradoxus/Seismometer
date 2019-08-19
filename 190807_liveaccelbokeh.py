#run with bokeh serve --show 190807_liveaccelbokeh.py

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource

import glob
import os
#from accelinfo import getfilepath

source = ColumnDataSource(data=dict(x=[], y=[],z=[],t=[]))
fg = figure(width=1000, plot_height=500, title="Acceleration",)

fg.line(x='t', y='x',color='red', source=source)
fg.circle(x='t', y='x',color='brown', source=source)
fg.line(x='t', y='y', color='blue', source=source)
fg.line(x='t', y='z',color='green', source=source)

fg.x_range.follow = "end"
fg.x_range.follow_interval = 5000
fg.x_range.range_padding=0

fg.xgrid.grid_line_color = None
fg.ygrid.grid_line_color = None
fg.background_fill_color = "snow"

curdoc().add_root(fg)

def update():
    #try:
        filename = max(glob.iglob('/home/nick/Documents/Code/*accel.csv'), key=os.path.getmtime)
        fa = open(filename, 'r')
        linelist = fa.readlines()
        fa.close()
        if len(linelist[-1]) < 56 or len(linelist[-1]) > 43:
            line = linelist[-1]
        else:
            return
        
        #line = fa.readline()
        line = line.replace('\"','')
        line = line.replace('\n','')
        line = line.split(',')
        
        #line[0].replace('"','')
        #line[1].strip('"')
        #line[2].strip('"')
        #line[3].strip('"')
        
        x = float(line[0])
        y = float(line[1])
        z = float(line[2])
        t = float(line[3])
    
        # construct the new values for all columns, and pass to stream
        new_data = dict(x=[x], y=[y],z=[z],t=[t])
        source.stream(new_data, rollover=5000)
    #except:
       # print('skippedline: ' + str(line))
        #pass

curdoc().add_periodic_callback(update, 5)
