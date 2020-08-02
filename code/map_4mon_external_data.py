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
from bokeh_template_external_js import template as template_ext_js

# %% General plotting settings
"""
# %% General plotting settings
________________________________________________________________________________
"""
plot_settings = {
    'toolbar_location':'above'
    }

# %% Assign output file
"""
# %% Assign output file
________________________________________________________________________________
"""
def filename(fullname):
    """ Return the name of a file without its path or extension"""
    return os.path.splitext(os.path.split(fullname)[1])[0]
output_filename = "../site/plots/"+os.path.basename(os.path.splitext(__file__)[0]) # name the output file/s after the script file
output_file(output_filename+".html",title=filename(output_filename))

# %% Get data
"""
# %%  Get data
________________________________________________________________________________
"""
data_path = './tmp_data/'
print('*** Load Processed Data From: '+data_path)
pbar.progress_bar(0,4)
DF_States_COVID     = pickle.load(open(data_path+"DF_States_COVID.p","rb"))
pbar.progress_bar(1,4)
DF_Counties_COVID   = pickle.load(open(data_path+"DF_Counties_COVID.p","rb"))
pbar.progress_bar(2,4)
DI_States_map     = pickle.load(open(data_path+"DI_States_map.p","rb"))
pbar.progress_bar(3,4)
DI_Counties_map   = pickle.load(open(data_path+"DI_Counties_map.p","rb"))
pbar.progress_bar(4,4)

# %% Convert into ColumnDataSource
"""
# %% Convert into ColumnDataSource
________________________________________________________________________________
"""
print('*** Convert Data into ColumnDataSource')
DS_States_COVID     = {}
DS_Counties_COVID   = {}
DS_Counties_map     = {}
DS_States_map       = {}

keep_map_data = {
    #['x', 'y', 'xc', 'yc', 'name', 'state_id', 'state_name', 'color', 'population', 'covid_data_labels', 'current_Absolute_positive', 'current_Absolute_death', 'current_Absolute_recovered', 'current_Absolute_positiveActive', 'current_positive', 'current_death', 'current_recovered', 'current_positiveActive', 'current_positiveActive_increase_mav', 'current_positive_increase_mav']
    'keys': ['x', 'y', 'name', 'state_name', 'population','number_of_counties', 'current_Absolute_positive', 'current_Absolute_death', 'current_Absolute_recovered', 'current_Absolute_positiveActive',  'current_positive_increase_mav'],
    }
print('Converting States COVID Data... (just used for max y tracking)')
N = len(DF_States_COVID)-1
max_pos = 10000; # track whats the maximum positive number per million (increment to find the nearest whole digit percentage)
for n,d in enumerate(DF_States_COVID):
    pbar.progress_bar(n, N)
    if len(DF_States_COVID[d]['positive'])>0:
        if max(DF_States_COVID[d]['positive'].values)>max_pos:
            max_pos = max_pos+10000
del DF_States_COVID


print('Converting Counties map Data...')
N = len(DI_Counties_map)-1
for n,d in enumerate(DI_Counties_map):
    pbar.progress_bar(n, N)
    DS_Counties_map[d] = ColumnDataSource({k: DI_Counties_map[d][k] for k in keep_map_data['keys'] if k in DI_Counties_map[d].keys()})
del DI_Counties_map

print('Converting States COVID Data...')
DS_States_map = ColumnDataSource({k: DI_States_map[k] for k in keep_map_data['keys'] if k in DI_States_map.keys()})
pbar.progress_bar(1, 1)
del DI_States_map

print('Conversions Completed.')



"""
# %% Load key_to_filename
________________________________________________________________________________
"""
ext_datafiles_path = '../site/plots/data/'
ext_datafiles = {}
with open(ext_datafiles_path+'key_to_filename.json') as f:
    ext_datafiles['key_to_filename'] = json.load(f)
ext_datafiles['path'] = 'data/'

"""
# %% Load json file for initiallization
________________________________________________________________________________
"""
state_name = 'Ohio' # get first key, i.e. state name
with open(ext_datafiles_path+ext_datafiles['key_to_filename'][state_name]) as f:
    init_data = json.load(f)['data']
init_data['date'] = pd.to_datetime(init_data['date'])
# Reduce the initial dataset to save Spacer
for k in init_data:
    init_data[k] = init_data[k][0:1]
DS_States_COVID[state_name] = ColumnDataSource(init_data)
# %% Make State graph for COVID data
"""
# %% Make State graph for COVID data
________________________________________________________________________________
"""
# Define the initia source
source  = ColumnDataSource(DS_States_COVID[state_name].data)

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

p_state_covid = figure(x_axis_type='datetime',y_axis_type="linear",
    title='(Tap a state on the map above to show the corresponding COVID data here)',
    #plot_width=800, plot_height=600,
    tools="pan,wheel_zoom,box_zoom,reset", active_scroll=None, active_drag='pan',
    toolbar_location=plot_settings['toolbar_location'],
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    visible=False,
    ) # Assign tools and make wheel_zoom default on


# Y left Axis, Draw vertical bars,
yleft = {
    'label':  "Bar Graph: # per Million",
    'source': source,
    'x': 'date',
    'y': ['positiveActive','death','recovered'],
    'color': ["blue","black","orange"],
    'legend_label': [
            "Positive Active",
            "Deaths",
            "Recovered"],
    'limits': ax_limits['yl'],
    }
yleft['name']=yleft['y']
vg = p_state_covid.vbar_stack(
        x=yleft['x'], stackers=yleft['y'], color=yleft['color'],
        legend_label=yleft['legend_label'],
        source=yleft['source'],
        alpha=0.8,
        width=timedelta(days=.6),
        name=yleft['name'],
        )
glyphs = glyphs + [g for g in vg]

p_state_covid.yaxis.axis_label = yleft['label']
p_state_covid.yaxis.formatter=NumeralTickFormatter(format="0,0.0")
p_state_covid.y_range = Range1d(start=yleft['limits'][0],end=yleft['limits'][1])#, bounds=yleft['limits'])

# Setup for Y right axis:
yright = {
    'label':    "Line Graphs: # increase per Million",
    'source':   source,
    'x':        'date',
    'limits':   ax_limits['yr'],
    'y_range_name' : 'yr_range',
    }
yright_each = {
    'y': [
        'positive_increase_mav',
        'positiveActive_increase_mav',
        'death_increase10_mav'
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
p_state_covid.extra_y_ranges[yright['y_range_name']] = Range1d(start=yright['limits'][0],end=yright['limits'][1])
p_state_covid.add_layout(LinearAxis(y_range_name=yright['y_range_name']), "right")
p_state_covid.yaxis[1].axis_label = yright['label']

for n,y in enumerate(yright_each['y']):
    glyphs.append(
        p_state_covid.line(
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
p_state_covid.add_layout(zero_span)

# Weekly span marks
ds = np.arange(ax_limits['x'][0],ax_limits['x'][1],dtype='datetime64[D]');
day = np.timedelta64(1,'D',timezone=None)
for d in ds:
    if ((np.timedelta64(ds.max()-d,timezone=None)/day)%7)==0:
            ts = (np.datetime64(d,timezone=None) - np.datetime64('1970-01-01T00:00:00',timezone=None)) / np.timedelta64(1, 's',timezone=None)
            wloc = ts*1000 # get the week mark location in a format compatible with annotations
            p_state_covid.add_layout(
                Span(location=wloc,
                      dimension='height', line_color='gray',
                      line_dash='dashed', line_width=2, line_alpha=0.5,
                    ))


# # X axis formatting:
# mm = [source.data['date'].min()- np.timedelta64(1,'D'), source.data['date'].max()+- np.timedelta64(1,'D')]
p_state_covid.x_range = Range1d( # Set the range of the axis
    ax_limits['x'][0],ax_limits['x'][1],bounds=ax_limits['x']
 )
# #p_state_covid.xaxis[0].ticker.desired_num_ticks =round(np.busday_count(np.datetime64(source.data['date'].min(),'D'),np.datetime64(source.data['date'].max(),'D'))/3); # prefer number of labels (divide by 7 for week)
p_state_covid.xaxis.major_label_orientation = -np.pi/3 # slant the labels
dtformat = "%b-%d";
p_state_covid.xaxis.formatter=formatter=DatetimeTickFormatter( # Always show the same date formatting regardless of zoom
    days=dtformat,
    months=dtformat,
    hours=dtformat,
    minutes=dtformat)

# Add legend
p_state_covid.legend.location = "top_left"

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
p_state_covid.add_tools(hover)

# # Extra formatting
# for ax in p_state_covid.yaxis:
#     ax.axis_label_text_font_style = 'bold'
#     ax.axis_label_text_font_size = '16pt'
# p_state_covid.title.text_font_size = '20pt'
# p_state_covid.title.text_font_style = 'italic'

glyphs_covid_state = glyphs
glyphs = []

# %% Make County graph for COVID data
"""
# %% Make County graph for COVID data
________________________________________________________________________________
"""
# Define the initia source
source  = ColumnDataSource(DS_States_COVID[state_name].data)

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

p_county_covid = figure(x_axis_type='datetime',y_axis_type="linear",
    title='Tap a county on the map above to show the corresponding population normalized COVID data time history',
    #plot_width=800, plot_height=600,
    tools="pan,wheel_zoom,box_zoom,reset", active_scroll=None, active_drag='pan',
    toolbar_location=plot_settings['toolbar_location'],
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    visible = False,
    ) # Assign tools and make wheel_zoom default on


# Y left Axis, Draw vertical bars,
yleft = {
    'label':  "Bar Graph: # per Million",
    'source': source,
    'x': 'date',
    'y': ['positiveActive','death','recovered'],
    'color': ["blue","black","orange"],
    'legend_label': [
            "Positive Active",
            "Deaths",
            "Recovered (estimated)"],
    'limits': ax_limits['yl'],
    }
yleft['name']=yleft['y']
vg = p_county_covid.vbar_stack(
        x=yleft['x'], stackers=yleft['y'], color=yleft['color'],
        legend_label=yleft['legend_label'],
        source=yleft['source'],
        alpha=0.8,
        width=timedelta(days=.6),
        name=yleft['name'],
        )
glyphs = glyphs + [g for g in vg]

p_county_covid.yaxis.axis_label = yleft['label']
p_county_covid.yaxis.formatter=NumeralTickFormatter(format="0,0.0")
p_county_covid.y_range = Range1d(start=yleft['limits'][0],end=yleft['limits'][1])#, bounds=yleft['limits'])

# Setup for Y right axis:
yright = {
    'label':    "Bar Graph: # per Million",
    'source':   source,
    'x':        'date',
    'limits':   ax_limits['yr'],
    'y_range_name' : 'yr_range',
    }
yright_each = {
    'y': [
        'positive_increase_mav',
        'positiveActive_increase_mav',
        'death_increase10_mav'
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
p_county_covid.extra_y_ranges[yright['y_range_name']] = Range1d(start=yright['limits'][0],end=yright['limits'][1])
p_county_covid.add_layout(LinearAxis(y_range_name=yright['y_range_name']), "right")
p_county_covid.yaxis[1].axis_label = yright['label']

for n,y in enumerate(yright_each['y']):
    glyphs.append(
        p_county_covid.line(
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
p_county_covid.add_layout(zero_span)

# Weekly span marks
ds = np.arange(ax_limits['x'][0],ax_limits['x'][1],dtype='datetime64[D]');
day = np.timedelta64(1,'D',timezone=None)
for d in ds:
    if ((np.timedelta64(ds.max()-d,timezone=None)/day)%7)==0:
            ts = (np.datetime64(d,timezone=None) - np.datetime64('1970-01-01T00:00:00',timezone=None)) / np.timedelta64(1, 's',timezone=None)
            wloc = ts*1000 # get the week mark location in a format compatible with annotations
            p_county_covid.add_layout(
                Span(location=wloc,
                      dimension='height', line_color='gray',
                      line_dash='dashed', line_width=2, line_alpha=0.5,
                    ))


# # X axis formatting:
# mm = [source.data['date'].min()- np.timedelta64(1,'D'), source.data['date'].max()+- np.timedelta64(1,'D')]
p_county_covid.x_range = Range1d( # Set the range of the axis
    ax_limits['x'][0],ax_limits['x'][1],bounds=ax_limits['x']
 )
# #p_county_covid.xaxis[0].ticker.desired_num_ticks =round(np.busday_count(np.datetime64(source.data['date'].min(),'D'),np.datetime64(source.data['date'].max(),'D'))/3); # prefer number of labels (divide by 7 for week)
p_county_covid.xaxis.major_label_orientation = -np.pi/3 # slant the labels
dtformat = "%b-%d";
p_county_covid.xaxis.formatter=formatter=DatetimeTickFormatter( # Always show the same date formatting regardless of zoom
    days=dtformat,
    months=dtformat,
    hours=dtformat,
    minutes=dtformat)

# Add legend
p_county_covid.legend.location = "top_left"

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
p_county_covid.add_tools(hover)

# Extra formatting
# for ax in p_county_covid.yaxis:
#     ax.axis_label_text_font_style = 'bold'
#     ax.axis_label_text_font_size = '16pt'
# p_county_covid.title.text_font_size = '20pt'
# p_county_covid.title.text_font_style = 'italic'

glyphs_covid_county = glyphs
glyphs = []

# %% Setup map of all counties
"""
%% Setup map of all counties
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
    out['formatter'] = FuncTickFormatter(
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
# %% Make Buttons for state graph
"""
# %% Make Buttons for state graph
________________________________________________________________________________
"""
buttons = {}
buttons['state_covid_data'] = Toggle(label="State Time History Graph",visible=False) #
buttons['state_covid_data'].js_on_change('active',CustomJS(args={'p_state_covid':p_state_covid},code="""
                  if (cb_obj.active == false){
                      cb_obj.label  = "Show State Time History Graph"
                      p_state_covid.visible = false
                  }
                  else{
                      cb_obj.label  = "Hide State Time History Graph"
                      p_state_covid.visible = true
                      }
                  """))


buttons['county_covid_data'] = Toggle(label="County Time History Graph", visible=False) #
buttons['county_covid_data'].js_on_change('active',CustomJS(args={'p_county_covid':p_county_covid},code="""
                  if (cb_obj.active == false){
                      cb_obj.label  = "Show County Time History Graph"
                      p_county_covid.visible = false
                  }
                  else{
                      cb_obj.label  = "Hide County Time History Graph"
                      p_county_covid.visible = true
                      }
                  """))

buttons['reset_county_covid_data'] = Button(label="Reset County Time History Graph", visible=False, button_type='primary')
buttons['reset_county_covid_data'].js_on_event(events.ButtonClick,CustomJS(args={'p_county_covid':p_county_covid},code="""
                  p_county_covid.reset.emit();
                  """))
buttons['reset_state_covid_data'] = Button(label="Reset State Time History Graph", visible=False, button_type='primary')
buttons['reset_state_covid_data'].js_on_event(events.ButtonClick,CustomJS(args={'p_state_covid':p_state_covid},code="""
                  p_state_covid.reset.emit();
                  """))

# %% Make map of all counties
"""
# %% Make map of all counties
________________________________________________________________________________
"""
p_county_map = figure(
    title="(Tap a county on the map above to show the corresponding data here)",
    tools= "pan,wheel_zoom,tap,reset,hover,save",active_tap='tap',
    toolbar_location=plot_settings['toolbar_location'],
    match_aspect=True,
    x_axis_location=None, y_axis_location=None,
    tooltips=[
        ('Name', "@name"),
        ("Population","@population{0,0.}"),
        ('Positive Cases',"@current_Absolute_positive{0,0.}"),
        ('Recovered Cases (est)',"@current_Absolute_recovered{0,0.}"),
        ('Positive Active Cases',"@current_Absolute_positiveActive{0,0.}"),
        ('Deaths',"@current_Absolute_death{0,0.}"),
    ],
    x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    visible = False,
    )
bztool = BoxZoomTool(match_aspect=True)
p_county_map.add_tools(bztool)
p_county_map.toolbar.active_drag=  None #bztool

tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p_county_map.add_tile(tile_provider)
p_county_map.grid.grid_line_color = None
p_county_map.hover.point_policy = "follow_mouse"
patches_counties = p_county_map.patches(
    'x', 'y', source=ColumnDataSource(DS_Counties_map[state_name].data),
    fill_color={'field': 'current_positive_increase_mav', 'transform': color_mapper},
    fill_alpha=0.6, line_color="white", line_width=1,
    )
p_county_map.add_layout(color_bar, 'right')


# Add taptool to select from which state to show all the counties
callbacktap = CustomJS(args={'index_to_state_name':DS_States_map.data['name'],
                             'glyphs_covid_county':glyphs_covid_county,
                             #'DS_Counties_COVID':DS_Counties_COVID,
                             'ext_datafiles': ext_datafiles,
                             'p_county_covid': p_county_covid,
                             'tb':[buttons['county_covid_data'],buttons['reset_county_covid_data']],
                             },
                       code="""
        if (cb_data.source.selected.indices.length>0){

            var ind = cb_data.source.selected.indices[0]
            var state_name  = cb_data.source.data['state_name'][0]
            var county_name = cb_data.source.data['name'][ind]
            var counte_state_name = county_name + ", "+state_name
            var county_id = county_name + ", "+state_name+", US"

            console.log(county_id)
            console.log(ext_datafiles['path'])
            console.log(ext_datafiles['key_to_filename'][county_id])
            var datafilename = ext_datafiles['path']+ext_datafiles['key_to_filename'][county_id]

            $.getJSON(datafilename,function(from_datafile){
                for (var i=0; i< glyphs_covid_state.length; i++){
                    glyphs_covid_county[i].data_source.data = from_datafile['data'] //DS_States_COVID[state_name].data
                    glyphs_covid_county[i].data_source.change.emit();
                    }
            });

            //p_county_covid.visible = true
            for (var i=0; i<tb.length; i++){
                    tb[i].visible  = true
            }
            p_county_covid.title.text = counte_state_name+": COVID data time history, population normalized"//  (Tap a county on the map above to show the corresponding data here)"
        }
        console.log(county_id)
                       """)
taptool = p_county_map.select(type=TapTool)
taptool.callback = callbacktap

#%% Make County map buttons
"""
# %% Make map of all counties
________________________________________________________________________________
"""
buttons['reset_county_map'] = Button(label="Reset Map of Counties", visible=False, button_type='warning')
buttons['reset_county_map'].js_on_event(events.ButtonClick,CustomJS(args={'p_county_map':p_county_map},code="""
                  p_county_map.reset.emit();
                  """))


# %% Make the States map
"""
# %% Make the States map
________________________________________________________________________________
"""
def minmax(xx):
    minxx = np.nanmin([np.nanmin(x) for x in xx])
    maxxx = np.nanmax([np.nanmax(x) for x in xx])
    return (minxx, maxxx)
p_state_map = figure(
    title="US States - Colors show last weeks average daily increase in positive cases per 1 million people in each area",
    #x_range=minmax(DS_States_map.data['xc']), y_range=minmax(DS_States_map.data['yc']),
    x_range=(-1.4e7,-7.4e6),
    y_range=(2.88e6,6.28e6),
    # sizing_mode='stretch_width',
    tools= "tap,pan,wheel_zoom,reset,save",active_tap='tap',
    toolbar_location=plot_settings['toolbar_location'],
    # x_axis_location=None, y_axis_location=None,
    x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode = 'scale_width',
    aspect_ratio = 2,
    match_aspect=True,
    )
p_state_map.grid.grid_line_color = None
bztool_s = BoxZoomTool(match_aspect=True)
p_state_map.add_tools(bztool_s)
p_state_map.toolbar.active_drag=  None #bztool_s

# Add the map tiles
tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p_state_map.add_tile(tile_provider)

# Add the states
patches_states = p_state_map.patches('x', 'y', source=DS_States_map,
          fill_color={'field': 'current_positive_increase_mav', 'transform': color_mapper},
          fill_alpha=0.6, line_color="white", line_width=1)
p_state_map.add_layout(color_bar, 'right')
# Add the hover tool to show the state name and number of counties
hoverm = HoverTool()
hoverm.tooltips=[
    ('Name', "@name"),
    ('Number Of Counties','@number_of_counties'),
    ("Population","@population{0,0.}"),
    #("Current COVID Statistics","{}".format('-'*15)),
    ('Positive Cases',"@current_Absolute_positive{0,0.}"),
    ('Recovered Cases',"@current_Absolute_recovered{0,0.}"),
    ('Positive Active Cases',"@current_Absolute_positiveActive{0,0.}"),
    ('Deaths',"@current_Absolute_death{0,0.}"),
]
p_state_map.add_tools(hoverm)

# Add taptool to select from which state to show all the counties
callbacktap = CustomJS(args={'patches_counties': patches_counties,
                             'index_to_state_name':DS_States_map.data['name'],
                             #'DS_Counties_map':DS_Counties_map,
                             'glyphs_covid_state':glyphs_covid_state,
                             #'DS_States_COVID':DS_States_COVID,
                             'ext_datafiles':ext_datafiles,
                             'p_county_map':p_county_map,
                             'p_state_covid':p_state_covid, # state covid data plot
                             'tb':[buttons['state_covid_data'],buttons['reset_state_covid_data'],buttons['reset_county_map']],
                             'datetime_made': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             },
                       code="""

        if (cb_data.source.selected.indices.length>0){
            var ind = cb_data.source.selected.indices[0]
            var state_name = index_to_state_name[ind]


            console.log('This file was made on: '+datetime_made)
            console.log(state_name)
            console.log(ext_datafiles['path'])
            console.log(ext_datafiles['key_to_filename'][state_name])
            var datafilename = ext_datafiles['path']+ext_datafiles['key_to_filename'][state_name]
            var datafilename_map = ext_datafiles['path']+ext_datafiles['key_to_filename'][state_name+'_map']
            console.log(datafilename)

            function rep_nan_code(dic,nan_code){
                var inds
                for (var key in dic){
                        dic[key] = array_element_replace(dic[key],nan_code,NaN)
                }
                return dic;
            }

            function array_element_replace(arr, old_value, new_value) {
                for (var i = 0; i < arr.length; i++) {
                    if (arr[i].length>1){
                        arr[i] =  array_element_replace(arr[i], old_value, new_value)
                    }
                    else{
                        if (arr[i] === old_value) {
                          arr[i] = new_value;
                        }
                    }
                }
                return arr;
            }

            function correct_date_format(dic,key='date'){
                const mul = 1e-6
                dic[key]=dic[key].map(function(a) {return a*mul;})
                return dic
            }

            console.log("Using jquary to fetch Covid data")
            $.getJSON(datafilename, function() {
              console.log( "success" );
            })
              .done(function(from_datafile) {
                console.log('Read file: '+datafilename)
                from_datafile['data'] = rep_nan_code(from_datafile['data'],from_datafile['nan_code'])
                from_datafile['data'] = correct_date_format(from_datafile['data'])

                for (var i=0; i< glyphs_covid_state.length; i++){
                    glyphs_covid_state[i].data_source.data = from_datafile['data'] //DS_States_COVID[state_name].data
                    glyphs_covid_state[i].data_source.change.emit();
                    }
                console.log('Updated to contents of: '+datafilename)              })
              .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ", " + error;
                console.log( "Request Failed: " + err );
                console.log(jqxhr)
              })
              .always(function() {
                //console.log( "complete the Always func" );
              });


            //console.log("Updating the state map")

            console.log("Using jquary to fetch map data")
            $.getJSON(datafilename_map, function() {
              console.log( "success" );
            })
              .done(function(from_datafile) {
                console.log('Read file: '+datafilename_map)
                from_datafile['data'] = rep_nan_code(from_datafile['data'],from_datafile['nan_code'])

                patches_counties.data_source.data = from_datafile['data']
                patches_counties.data_source.change.emit(); // Update the county patches
                p_county_map.reset.emit(); // Reset the county figure, otherwise panning and zooming on that fig will persist despite the change

                console.log('Updated to contents of: '+datafilename_map)
                })
              .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ", " + error;
                console.log( "Request Failed: " + err );
                console.log(jqxhr)
              })
              .always(function() {
                //console.log( "complete the Always func" );
              });


            //patches_counties.data_source.data = DS_Counties_map[state_name].data
            //patches_counties.data_source.change.emit(); // Update the county patches
            //p_county_map.reset.emit(); // Reset the county figure, otherwise panning and zooming on that fig will persist despite the change

            p_county_map.visible   = true

            for (var i=0; i<tb.length; i++){
                    tb[i].visible  = true
            }
            //p_state_covid.visible = true
            p_state_covid.title.text = state_name+": COVID data time history, population normalized"//   (Tap a state on the map above to show the corresponding data here)"
        }
        console.log(state_name)
                       """)
taptool = p_state_map.select(type=TapTool)
taptool.callback = callbacktap

#%% Make State map buttons
"""
#%% Make State map buttons
________________________________________________________________________________
"""
buttons['reset_state_map'] = Button(label="Reset Map of States", visible=True, button_type='warning')
buttons['reset_state_map'].js_on_event(events.ButtonClick,CustomJS(args={'p_state_map':p_state_map},code="""
                  p_state_map.reset.emit();
                  """))


# %% Make heading for the whole thing
"""
# %% Make heading for the whole thing
"""
heading = Div(text="""
<h1> US State And County Maps Of COVID Data With Population Normalized Time History </h1>
<p_county_map>Shows all the US states colored according to last weeks average number of new COVID-19 cases per day with state population normalization  (number of people per million).</p_county_map>
<ul>
	<li>Higher color number corresponds to faster spread of the virus.</li>
    <li>On the top right of each graph thera are tools to zoom/pan/reset/save.</li>
	<li>On Mobile: Use two finger to scroll the page.</li>
    <li>Data last updated on: {data_update} </li>
    <li>Graphs generated on: {graph_update} </li>
    <li>Recovery data for counties is unavailable.  Using estimates of approx 15days to recovery for those that don't die.</li>
</ul>

<h3> Tap on any state to show same kind of map of all counties below </h3>
""".format(
    data_update = pd.to_datetime(DS_States_COVID[state_name].data['date'][-1]).strftime('%Y-%m-%d'),
    graph_update =pd.Timestamp.now().strftime('%Y-%m-%d'),
    ))

footer = Div(text="""
<h3> Sources </h3>
<ul>
    <li>GitHub repository for this project: <a href="https://github.com/thedrdos/covid-map"> https://github.com/thedrdos/covid-map </a>. </li>
    <li>Produced using Python with Bokeh and other modules.</li>
	<li>State and County Geographical Data from <a href="http://www2.census.gov/geo/tiger/">The US Census Bureau</a>.</li>
	<li>COVID-19 Data on States from <a href="https://covidtracking.com">The COVID Tracking Project</a>
     or on <a href="https://github.com/COVID19Tracking/covid-tracking-data">GitHub</a>.</li>
	<li>COVID-19 Data on Counties from <a href="https://coronavirus.jhu.edu">The John Hopkins University Coronavirus Resource Center</a>
     or on <a href="https://github.com/CSSEGISandData/COVID-19">GitHub</a>.</li>
</ul>
""")


# %% Combine all the graphs
"""
# %% Combine all the graphs
________________________________________________________________________________
"""

# Layout the figures and show them
p_state_covid.visible = True
p_state_map.sizing_mode = 'scale_width'
p_state_covid.sizing_mode = 'scale_width'
p_county_map.sizing_mode = 'scale_width'
p_county_covid.sizing_mode = 'scale_width'
#layout = column(heading,p_state_map,buttons['state_covid_data'],p_state_covid,p_county_map,buttons['county_covid_data'],p_county_covid,footer,sizing_mode='scale_width')
# layout = column(row(p_state_map,p_state_covid,sizing_mode='scale_width'),row(p_county_map,p_county_covid,sizing_mode='scale_width'),sizing_mode='scale_width')
layout = column(heading,
                p_state_map,
                row(buttons['reset_state_map'],buttons['state_covid_data'],buttons['reset_state_covid_data'],sizing_mode='scale_width',
                    margin=(0,20,0,20),
                    ),
                p_state_covid,
                p_county_map,
                row(buttons['reset_county_map'],buttons['county_covid_data'],buttons['reset_county_covid_data'],sizing_mode='scale_width',
                    margin=(0,20,0,20),
                    ),
                p_county_covid,
                footer,
                sizing_mode='scale_width')
layout.margin = (0,24,0,24) # top, right, bottom, left
save(layout,template=template_ext_js('jquary'))
view(output_filename+'.html')
