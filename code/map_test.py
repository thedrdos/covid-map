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
from bokeh.models import Select
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
from bokeh.models import LogAxis, LinearAxis, Range1d, DataRange1d # for adding the second axis
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
with gzip.GzipFile(ext_datafiles['path']+'location_to_mapfilename.json.gz', 'r') as fin:
    ext_datafiles['location_to_mapfilename'] = json.loads(fin.read().decode('utf-8'))

"""
# %% Load json file for initiallization
________________________________________________________________________________
"""
max_pos = 10000; # track whats the maximum positive number per million (increment to find the nearest whole digit percentage)
for l in ext_datafiles['location_to_filename']:
    if l not in ['Earth']:
        with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][l]+'.json.gz', 'r') as fin:
            datafile = json.loads(fin.read().decode('utf-8'))
            #data = dic_nan_decode(datafile['data'],datafile['nan_code'])
            data =datafile['data']
            if len(data['positivePerMil'])>0:
                if max(data['positivePerMil'])>max_pos:
                    max_pos +=10000;


init_location = 'Italy' #'US'# get first key, i.e. state name
with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][init_location]+'.json.gz', 'r') as fin:
    init_datafile = json.loads(fin.read().decode('utf-8'))
init_data= dic_nan_decode(init_datafile['data'],init_datafile['nan_code'])
init_data['date'] = pd.to_datetime(init_data['date'])
latest_data_date = max(init_data['date'])
source_data = ColumnDataSource(init_data)

init_location = 'Earth'#
with gzip.GzipFile(ext_datafiles['path']+ext_datafiles['location_to_filename'][init_location]+'_map.json.gz', 'r') as fin:
    init_mapfile = json.loads(fin.read().decode('utf-8'))
init_map = init_mapfile['data']

source_map = ColumnDataSource(init_map)




"""
# %% Make color mapping and ticks
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
    label_standoff=2, border_line_color=None,
    location=(0,0),
    bar_line_alpha = 0.5,
    major_label_text_align = 'left',
    )

"""
# %% Make figure
________________________________________________________________________________
"""
p2 = figure(
    title="(Tap on the graph to select a date, then update the map with the data for that date)",
    tools= "pan,wheel_zoom,tap,reset,hover,save",active_tap='tap',
    #toolbar_location=plot_settings['toolbar_location'],
    x_axis_type='datetime',y_axis_type="linear",
    sizing_mode = 'scale_width',
     aspect_ratio = 3,
    visible = True,
    )
line = p2.line(x='date',y='positiveActivePerMil',source=source_data)



p = figure(
    title="(Tap a county on the map above to show the corresponding data here)",
    tools= "pan,wheel_zoom,tap,reset,hover,save",active_tap='tap',
    #toolbar_location=plot_settings['toolbar_location'],
    # x_range=(-1.4e7,-7.4e6),
    # y_range=(2.88e6,6.28e6),
    match_aspect=True,
    #x_axis_location=None, y_axis_location=None,
    #x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode = 'scale_width',
    aspect_ratio = 1.66,
    visible = True,
    )
tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p.add_tile(tile_provider)
p.grid.grid_line_color = None
# p.x_range = DataRange1d(start=-1.4e7,end=-7.4e6)
p.x_range = DataRange1d()

bztool = BoxZoomTool(match_aspect=True)
p.add_tools(bztool)
p.toolbar.active_drag=  None #bztool

mpoly = p.multi_polygons(
    'x', 'y', source=source_map,
    fill_color={'field': 'positiveIncreaseMAVPerMil', 'transform': color_mapper},
    fill_alpha=0.6,
    line_color="white",
    line_width=1,
    )

with open(javascript_path+'map_callback.js','r') as f:
    map_callback = f.read()
for ev in ['tap','doubletap']:
    p.js_on_event(ev, CustomJS(args={
                              'event':ev,
                              'mpoly':mpoly,
                              'ext_datafiles': ext_datafiles,
                              'source_map': source_map,
                              'line':line,
                              },code=map_callback))

opts = [k for k in init_map.keys() if isinstance(init_map[k][0],int) or isinstance(init_map[k][0],float) ]

select = Select(title="Data Options:", value="positiveActiveMAVPerMil", options=opts)
select.js_on_change("value", CustomJS(args={
                              'mpoly':mpoly,
                              'ext_datafiles': ext_datafiles,
                              'line':line,
                              },code="""
    console.log('select: value=' + this.value, this.toString())
    mpoly.glyph.fill_color.field = this.value
    mpoly.data_source.change.emit()
    console.log(mpoly.glyph.fill_color.transform)
    console.log(mpoly.glyph.fill_color.transform.low)
    console.log(mpoly.glyph.fill_color.transform.high)
"""))

with open(javascript_path+'graph_callback.js','r') as f:
    graph_callback = f.read()
p2.js_on_event('tap', CustomJS(args={
                              'mpoly':mpoly,
                              'ext_datafiles': ext_datafiles,
                              'line':line,
                              },code=graph_callback))

opts = [k for k in init_data.keys() if isinstance(init_data[k][0],int) or isinstance(init_data[k][0],float) ]

select2 = Select(title="Data Options:", value="positiveActiveMAVPerMil", options=opts)
select2.js_on_change("value", CustomJS(args={
                              'mpoly':mpoly,
                              'ext_datafiles': ext_datafiles,
                              'line':line,
                              },code="""
    console.log('select: value=' + this.value, this.toString())
    line.glyph.y.field = this.value
    line.data_source.change.emit()

"""))
"""
# %% Combine all the graphs
________________________________________________________________________________
"""

# Layout the figures and show them
layout = column(row(select,p),row(select2,p2),
                sizing_mode='scale_width')
layout.margin = (4,20,4,20) # top, right, bottom, left
save(layout,template=template_ext_js(['jquary','pako']))
#view('http://localhost:7800/'+output_filename+'.html')
