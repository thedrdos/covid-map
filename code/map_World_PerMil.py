#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Jul 2020

@author: TheDrDOS
"""
# # Clear the Spyder console and variables
# try:
#     from IPython import get_ipython
#     get_ipython().magic('clear')
#     get_ipython().magic('reset -f')
# except:
#     pass


from bokeh.io import show, save, output_file
from bokeh.util.browser import view
from bokeh.models import ColorBar, ColorMapper, LogColorMapper,LogTicker, LinearColorMapper
from bokeh.models import BasicTicker as LinearTicker
from bokeh.models import BasicTickFormatter, LogTicker, FixedTicker, FuncTickFormatter
from bokeh.palettes import Magma11 as palette
from bokeh.palettes import Inferno256, Turbo256
from bokeh.plotting import figure
from bokeh.models import Div
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool,BoxZoomTool # for showing the hover tool

from bokeh_template_external_js import template as template_ext_js

from bokeh import events
from bokeh.models import  Label, LabelSet, CustomJS, TapTool, Toggle, Button, Spacer
from bokeh.tile_providers import CARTODBPOSITRON_RETINA, get_provider
import os

import numpy as np
import datetime
from datetime import date, timedelta

from bokeh.models import NumeralTickFormatter, BasicTickFormatter
from bokeh.models import LogAxis, LinearAxis, Range1d # for adding the second axis
from bokeh.models  import DatetimeTickFormatter # for formatting the dates on the x axis

from bokeh.layouts import column, row, gridplot # For show multiple figures


from bokeh.models import Span # For adding spans (vertical/horizontal lines without end points)

import pandas as pd

import pickle
import progress_bar as pbar

import json
import gzip

import sys

# %% General plotting settings
"""
# %% General plotting settings
________________________________________________________________________________
"""
plot_settings = {
    'toolbar_location':'left'
    }

# %% Assign output file
"""
# %% Assign output file
________________________________________________________________________________
"""
def filename(fullname):
    """ Return the name of a file without its path or extension"""
    return os.path.splitext(os.path.split(fullname)[1])[0]
this_filename = filename(os.path.basename(os.path.splitext(__file__)[0]))
javascript_path = './'+this_filename+'_js/'
localhost_path  = './plots/'
output_filename = "./../site/plots/"+this_filename # name the output file/s after the script file
output_file(output_filename+".html",
    title="Interactive Map of USA COVID19 Data with Time History")#title=filename(output_filename))

# %%
"""
# Support functions
________________________________________________________________________________
"""
def dic_nan_decode(d,nan_code):
    for k in d:
        d[k] = array_element_replace(d[k],nan_code,float('NaN'))
    return d

def array_element_replace(arr, old_value, new_value):
    for i in range(0,len(arr)):
        if isinstance(arr[i],list):
            arr[i] = array_element_replace(arr[i],old_value,new_value)
        else:
            if arr[i]==old_value:
                arr[i]=new_value
    return arr

# %% Get data
"""
# %%  Get data
________________________________________________________________________________
"""
"""
# %% Load key_to_filename
________________________________________________________________________________
"""
# Load with compression
ext_datafiles = {
    'path': "../site/plots/data/",
    'rel_path': "./data/",
    }
with gzip.GzipFile(ext_datafiles['path']+'filename_to_location.json.gz', 'r') as fin:
    ext_datafiles['filename_to_location'] = json.loads(fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path']+'location_to_filename.json.gz', 'r') as fin:
    ext_datafiles['location_to_filename'] = json.loads(fin.read().decode('utf-8'))


"""
# %% Load json file for initiallization
________________________________________________________________________________
"""
max_pos = 10000; # track whats the maximum positive number per million (increment to find the nearest whole digit percentage)
for l in ext_datafiles['location_to_filename']:
    if ('US' not in l and 'Earth' not in l) or l=='US':
        with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][l]+'.json.gz', 'r') as fin:
            datafile = json.loads(fin.read().decode('utf-8'))
            #data = dic_nan_decode(datafile['data'],datafile['nan_code'])
            data =datafile['data']
            if len(data['positivePerMil'])>0:
                if max(data['positivePerMil'])>max_pos and datafile['extra']['population']>100e3:
                    max_pos +=10000;
                    #print(l)
                    #print(max(data['positivePerMil']))


init_location = 'US' # get location
with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][init_location]+'.json.gz', 'r') as fin:
    init_datafile = json.loads(fin.read().decode('utf-8'))
init_data= dic_nan_decode(init_datafile['data'],init_datafile['nan_code'])
init_data['date'] = pd.to_datetime(init_data['date'])
latest_data_date = max(init_data['date'])

init_location = 'Earth' # get location
with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][init_location]+'_map.json.gz', 'r') as fin:
    init_mapfile = json.loads(fin.read().decode('utf-8'))
init_map = init_mapfile['data']

# Create source data structure and initialize state map
source_world_data = ColumnDataSource(init_data)
source_world_map = ColumnDataSource(init_map)
# Erase the underlying data to reduce the html filesize (will be loaded upon user tap feedback)
source_world_data.data  = {k:[] for k in source_world_data.data}

"""
# %% Make State graph for COVID data
________________________________________________________________________________
"""

# Set Axis limits
ax_limits = {
    'x':(
        pd.Timestamp.now()-pd.DateOffset(months=4),
        pd.Timestamp.now()
        ),
    'yl':(
        0, max_pos #1e6*5/100
        ),
    'yr':(
        -100, 500
        )
    }

# Make the bar and line plots
glyphs = []

p_world_covid = figure(x_axis_type='datetime',y_axis_type="linear",
    title='(Tap a state on the map above to show the corresponding COVID data here)',
    #plot_width=800, plot_height=600,
    tools="ypan,xpan,ywheel_zoom,xwheel_zoom,ybox_zoom,xbox_zoom,box_zoom,reset", active_scroll=None, active_drag='ypan',
    toolbar_location=plot_settings['toolbar_location'],
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    visible=False,
    ) # Assign tools and make wheel_zoom default on


# Y left Axis, Draw vertical bars,
yleft = {
    'label':  "Bar Graph: # per Million",
    'source': source_world_data,
    'x': 'date',
    'y': ['positiveActivePerMil','deathPerMil','recoveredPerMil'],
    'color': ["blue","black","orange"],
    'legend_label': [
            "Positive Active",
            "Deaths",
            "Recovered (estimated)"],
    'limits': ax_limits['yl'],
    }
yleft['name']=yleft['y']
vg = p_world_covid.vbar_stack(
        x=yleft['x'], stackers=yleft['y'], color=yleft['color'],
        legend_label=yleft['legend_label'],
        source=yleft['source'],
        alpha=0.8,
        width=timedelta(days=.6),
        name=yleft['name'],
        )
glyphs = glyphs + [g for g in vg]

p_world_covid.yaxis.axis_label = yleft['label']
p_world_covid.yaxis.formatter=NumeralTickFormatter(format="0,0.0")
p_world_covid.y_range = Range1d(start=yleft['limits'][0],end=yleft['limits'][1])#, bounds=yleft['limits'])

# Setup for Y right axis:
yright = {
    'label':    "Line Graphs: # increase per Million",
    'source':   source_world_data,
    'x':        'date',
    'limits':   ax_limits['yr'],
    'y_range_name' : 'yr_range',
    }
yright_each = {
    'y': [
        'positiveIncreaseMAVPerMil',
        'positiveActiveIncreaseMAVPerMil',
        'deathIncreaseMAV10PerMil'
        ],
    'legend_label': [
        'Positive Increase (week avg)',
        'Positive Active Increase (week avg)',
        'Deaths Increase x10 (week avg)'
        ],
    'line_color':[
        'red',#mapper,
        'yellowgreen',#color_mapper,
        'black'],
    'line_width':[
        4,8,4
        ],
    'line_dash': [
        'solid','solid','solid'],
    'name': ['' for i in range(0,3)],
    }
for n,y in enumerate(yright_each['y']):
    yright_each['name'][n] = y


# Make Y Right Axis:
p_world_covid.extra_y_ranges[yright['y_range_name']] = Range1d(start=yright['limits'][0],end=yright['limits'][1])
p_world_covid.add_layout(LinearAxis(y_range_name=yright['y_range_name']), "right")
p_world_covid.yaxis[1].axis_label = yright['label']

for n,y in enumerate(yright_each['y']):
    glyphs.append(
        p_world_covid.line(
            y_range_name=yright['y_range_name'],
            source=yright['source'],
            x=yright['x'],
            y=yright_each['y'][n],
            legend_label    = yright_each['legend_label'][n],
            line_color      = yright_each['line_color'][n],
            color      = yright_each['line_color'][n],
            line_width      = yright_each['line_width'][n],
            line_dash       = yright_each['line_dash'][n],
            name            = yright_each['name'][n],
        )
    )

# Horizontal right axis zero span
zero_span = Span(
    location=0, # Span the 0 line of the right y axis
                    dimension='width', line_color='gray',
                    line_dash='solid', line_width=3, line_alpha=0.4,
                    y_range_name=yright['y_range_name']
                    )
p_world_covid.add_layout(zero_span)

# Weekly span marks
ds = np.arange(ax_limits['x'][0],ax_limits['x'][1],dtype='datetime64[D]');
# use of timezones was depricated, before timezone=None was needed
day = np.timedelta64(1,'D')
for d in ds:
    if ((np.timedelta64(ds.max()-d)/day)%7)==0:
            ts = (np.datetime64(d) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
            wloc = ts*1000 # get the week mark location in a format compatible with annotations
            p_world_covid.add_layout(
                Span(location=wloc,
                      dimension='height', line_color='gray',
                      line_dash='dashed', line_width=2, line_alpha=0.5,
                    ))


# # X axis formatting:
# mm = [source.data['date'].min()- np.timedelta64(1,'D'), source.data['date'].max()+- np.timedelta64(1,'D')]
p_world_covid.x_range = Range1d( # Set the range of the axis
    ax_limits['x'][0],ax_limits['x'][1],#bounds=ax_limits['x']
 )
# #p_world_covid.xaxis[0].ticker.desired_num_ticks =round(np.busday_count(np.datetime64(source.data['date'].min(),'D'),np.datetime64(source.data['date'].max(),'D'))/3); # prefer number of labels (divide by 7 for week)
p_world_covid.xaxis.major_label_orientation = -np.pi/3 # slant the labels
dtformat = "%b-%d";
p_world_covid.xaxis.formatter=formatter=DatetimeTickFormatter( # Always show the same date formatting regardless of zoom
    days=dtformat,
    months=dtformat,
    hours=dtformat,
    minutes=dtformat)

# Add legend
p_world_covid.legend.location = "top_left"

# Add a hover tool
hover = HoverTool()
hover.tooltips=[
    #('Type', "$name"),
    ('', '$name: @$name{0,0.} on @date{%a-%b-%d}'),
]
# hover.mode = 'vline'
hover.formatters={
        '@date'     : 'datetime', # use 'datetime' formatter for '@date' field
        '$name'     : 'printf' # use 'printf' formatter for the name of the column
    }
hover.renderers = glyphs
p_world_covid.add_tools(hover)

# # Extra formatting
# for ax in p_world_covid.yaxis:
#     ax.axis_label_text_font_style = 'bold'
#     ax.axis_label_text_font_size = '16pt'
# p_world_covid.title.text_font_size = '20pt'
# p_world_covid.title.text_font_style = 'italic'

glyphs_covid_world = glyphs

# %% Make Buttons for state graph
"""
# %% Make Buttons for state graph
________________________________________________________________________________
"""
buttons = {}
buttons['state_covid_data'] = Toggle(label="Hide Time History Graph",visible=False, button_type='primary') #
buttons['state_covid_data'].js_on_change('active',CustomJS(args={'p_world_covid':p_world_covid},code="""
                  if (cb_obj.active == false){
                      cb_obj.label  = "Show Time History Graph"
                      p_world_covid.visible = false
                  }
                  else{
                      cb_obj.label  = "Hide Time History Graph"
                      p_world_covid.visible = true
                      }
                  """))
buttons['reset_world_covid_data'] = Button(label="Reset Time History Graph", visible=False, button_type='default')
buttons['reset_world_covid_data'].js_on_event(events.ButtonClick,CustomJS(args={'p_world_covid':p_world_covid},code="""
                  p_world_covid.reset.emit();
                  """))
"""
%% Setup color map
________________________________________________________________________________
"""
def Reverse(tuples):
    new_tup = tuples[::-1]
    return new_tup

def make_color_mapper_and_ticks(palette,low=0,high=1,tick_decimals = 2, label_format='{:1.0f}',label_separator='-',label_end="> ",label_start="< "):
    """
    Make a color mapper and custom range based colorbar (uses Javascripting)
    Parameters
    ----------
    palette : Bokeh palette
    low : number, optional
        low end of the color range (used in LinearColorMapper(palette=palette,low=low,high=high) ) . The default is 0.
    high : TYPE, optional
        high end of the color range (used in LinearColorMapper(palette=palette,low=low,high=high) ). The default is 1.
    tick_decimals : integer, optional
        Number of decimals to use when generating a list of tick marks (internal, can affect accuracy of ticks). The default is 2.
    label_format : string, optional
        Formatting of the labels . The default is '{:1.0f}'.
    label_separator : string, optional
        Separator used when generating the labels. The default is '-'.
    label_end : string, optional
        Used on the end label, since the range extends to all larger numberes. The default is "> ".
    label_start : string, optional
        Used on the start label, since the range extends to all lower numbers. The default is "< ".

    Returns
    -------
    Dictionary with keys:
        'color_mapper'   - LinearColorMapper(palette=palette,low=low,high=high)
        'ticker'         - FixedTicker(ticks=ticks)
        'formatter'      - FuncTickFormatter with custom Javascript code to make the ranges

    Example use:
        CmapAndTicks = make_color_mapper_and_ticks(palette=Spectral11 ,low=-100,high=340)
        color_bar = ColorBar(color_mapper=CmapAndTicks['color_mapper'],
                            ticker=CmapAndTicks['ticker'],
                            formatter=CmapAndTicks['formatter'])
     """
    N = len(palette)
    D=high-low;
    ticks = [low+(i+0.5)*D/N for i in range(0,N)]
    out = {}
    out['ticker'] = FixedTicker(ticks=ticks)
    labs = [label_format.format(low+(i)*D/N)+label_separator+ label_format.format(low+(i+1)*D/N) for i in range(0,N)]
    labs[0] = label_start+label_format.format(ticks[0]+0.5*D/N)
    labs[-1] = label_end+label_format.format(ticks[-1]-0.5*D/N)
    ticks_str = [('{:0.'+str(tick_decimals)+'f}').format(t) for t in ticks]
    data = dict(zip(ticks_str,labs))
    out['ticks'] = ticks
    out['data'] = data
    out['formatter'] = FuncTickFormatter( # Uses the python generated dictionary of ticks and labels, finding the nearest tick in the list of keys, and returning the value (i.e. the associated python generated label). I could rewrite this to be done just in Javascript https://docs.bokeh.org/en/latest/docs/reference/models/formatters.html
        code="""
        var data = {data}
        var keys = Object.keys(data).map(Number) // Get all the ticks that are to be labeled
        keys.sort((a, b) => {{        // Sort the keys, the 0 element will be the closest to the listed tick values
            return Math.abs(tick - a) - Math.abs(tick - b); }} )
        var key = keys[0].toFixed({decimals})
        return data[key]
    """.format(data= data, decimals= str(tick_decimals)))
    out['color_mapper'] = LinearColorMapper(palette=palette,low=low,high=high)
    return out

# Make colormap
#palette = tuple([p_county_map for p_county_map in palette]+['#ffffee'])
# palette = Reverse(Inferno256[128:-1:5])
palette = Turbo256[128:-1:5]

CmapAndTicks = make_color_mapper_and_ticks(
    palette=palette,
    low=0,high=20*len(palette),label_format='{:1.0f}')
color_mapper = CmapAndTicks['color_mapper']

color_bar = ColorBar(
    color_mapper=CmapAndTicks['color_mapper'],
    ticker=CmapAndTicks['ticker'],
    formatter=CmapAndTicks['formatter'],
    label_standoff=2, border_line_color=None, location=(0,0),
    bar_line_alpha = 0.5,
    major_label_text_align = 'left',
    )

# %% Make the States map
"""
# %% Make the States map
________________________________________________________________________________
"""
def minmax(xx):
    minxx = np.nanmin([np.nanmin(x) for x in xx])
    maxxx = np.nanmax([np.nanmax(x) for x in xx])
    return (minxx, maxxx)
p_world_map = figure(
    title="World - Colors show last weeks average daily increase in positive cases per 1 million people in each area",
    #x_range=minmax(DS_worlds_map.data['xc']), y_range=minmax(DS_worlds_map.data['yc']),
    # x_range=(-1.4e7,-7.4e6),
    # y_range=(2.88e6,6.28e6),
    # sizing_mode='stretch_width',
    tools= "tap,pan,wheel_zoom,reset,save",active_tap='tap',
    toolbar_location=plot_settings['toolbar_location'],
    # x_axis_location=None, y_axis_location=None,
    x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    match_aspect=True,
    )
p_world_map.grid.grid_line_color = None
bztool_s = BoxZoomTool(match_aspect=True)
p_world_map.add_tools(bztool_s)
p_world_map.toolbar.active_drag=  None #bztool_s

# Add the map tiles
tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p_world_map.add_tile(tile_provider)

# Add the states
# patches_worlds = p_world_map.patches('x', 'y', source=DS_worlds_map,
#           fill_color={'field': 'current_positive_increase_mav', 'transform': color_mapper},
#           fill_alpha=0.6, line_color="white", line_width=1)
patches_worlds = p_world_map.multi_polygons(
    xs='x', ys='y', source=source_world_map,
    fill_color={'field': 'positiveIncreaseMAVPerMil', 'transform': color_mapper},
    fill_alpha=0.6,
    line_color="white",
    line_width=1,
    )
p_world_map.add_layout(color_bar, 'right')
# Add the hover tool to show the state name and number of counties
hoverm = HoverTool()
hoverm.tooltips=[
    ('Name', "@name"),
    ("Population","@population{0,0.}"),
    #("Current COVID Statistics","{}".format('-'*15)),
    ('Positive Cases',"@positive{0,0.}"),
    ('Recovered Cases',"@recovered{0,0.}"),
    ('Positive Active Cases',"@positiveActive{0,0.}"),
    ('Deaths',"@death{0,0.}"),
]
p_world_map.add_tools(hoverm)

# Add taptool to select from which state to show all the counties
with open(javascript_path+'callback_world_map.js','r') as f:
    callback_world_map = f.read()
callbacktap = CustomJS(args={'index_to_world_name':init_map['name'],
                             'glyphs_covid_world':glyphs_covid_world,
                             'ext_datafiles':ext_datafiles,
                             'p_world_covid':p_world_covid, # state covid data plot
                             'tb':[buttons['state_covid_data'],buttons['reset_world_covid_data'],p_world_covid],
                             'datetime_made': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             },
                       code=callback_world_map)
taptool = p_world_map.select(type=TapTool)
taptool.callback = callbacktap

#%% Make State map buttons
"""
#%% Make State map buttons
________________________________________________________________________________
"""
buttons['reset_world_map'] = Button(label="Reset Map", visible=True, button_type='warning')
buttons['reset_world_map'].js_on_event(events.ButtonClick,CustomJS(args={'p_world_map':p_world_map},code="""
                  p_world_map.reset.emit();
                  """))
"""
# %% Make data graphs reset on doubletap
"""
for p in [p_world_covid]:
    p.js_on_event('doubletap',CustomJS(args={'p':p,},code="""
    p.reset.emit()
    """))


# %% Make heading for the whole thing
"""
# %% Make heading for the whole thing
"""
heading = Div(text="""
<h1> Wold Map Of COVID Data With Population Normalized Time History </h1>
<p>Shows all the countries colored according to last weeks average number of new COVID-19 cases per day with country population normalization  (number of people per million).</p>
<ul>
	<li>Higher color number corresponds to faster spread of the virus.</li>
    <li>On the left of each graph thera are tools to zoom/pan/reset/save.</li>
	<li>On Mobile: Use two finger to scroll the page.</li>
    <li>Data last updated on: {data_update} </li>
    <li>Graphs generated on: {graph_update} </li>
    <li>Recovery data for countries is unavailable.  Using estimates of approx 15days to recovery for those that don't die.</li>
</ul>

<h3> Tap on any country to show the COVID19 data time history graph below. </h3>
""".format(
    data_update = pd.to_datetime(latest_data_date).strftime('%Y-%m-%d'),
    graph_update =pd.Timestamp.now().strftime('%Y-%m-%d'),
    ))

footer = Div(text="""
<h3> Sources </h3>
<ul>
    <li>GitHub repository for this project: <a href="https://github.com/thedrdos/covid-map"> https://github.com/thedrdos/covid-map </a>. </li>
    <li>Produced using Python with Bokeh and other modules.</li>
	<li>Country geographical Data from <a href="http://www.naturalearthdata.com/">Natural Earth</a>.</li>
	<li>COVID-19 Data on Countries from <a href="https://coronavirus.jhu.edu">The John Hopkins University Coronavirus Resource Center</a>
     or on <a href="https://github.com/CSSEGISandData/COVID-19">GitHub</a>.</li>
</ul>
""")


# %% Combine all the graphs
"""
# %% Combine all the graphs
________________________________________________________________________________
"""

# Layout the figures and show them
p_world_map.sizing_mode = 'scale_width'
p_world_covid.sizing_mode = 'scale_width'
layout = column(heading,
                row(p_world_map,sizing_mode='scale_width'),
                row(buttons['reset_world_map'],buttons['state_covid_data'],buttons['reset_world_covid_data'],sizing_mode='scale_width',margin=(0,20,0,20),
                    ),
                p_world_covid,
                row(footer,sizing_mode='scale_width'),
                sizing_mode='scale_width')
layout.margin = (4,20,4,20) # top, right, bottom, left
save(layout,template=template_ext_js(['jquary','pako']))
# view(output_filename+'.html')
# view('http://localhost:7800/'+localhost_path+this_filename+'.html')
