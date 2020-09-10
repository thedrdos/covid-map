from bokeh.io import show, save, output_file
from bokeh.util.browser import view
from bokeh.models import ColorBar, ColorMapper, LogColorMapper,LogTicker, LinearColorMapper
from bokeh.models import BasicTicker as LinearTicker
from bokeh.models import BasicTickFormatter, LogTicker, FixedTicker, FuncTickFormatter
from bokeh.palettes import Inferno256, Turbo256, Colorblind8
from bokeh.plotting import figure
from bokeh.models import Div
from bokeh.models import ColumnDataSource
from bokeh.models import Select
from bokeh.models.tools import HoverTool,BoxZoomTool # for showing the hover tool
from bokeh.models.widgets import Tabs, Panel

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


""" %% Get data ------------------------------------------------------------"""
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

# Load json file for initiallization
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




""" %% Make color mapping and ticks ---------------------------------------- """
map_palette = Turbo256[128:-1:5]
graph_palette = Colorblind8

map_color_mapper = LinearColorMapper(palette=map_palette,low=0,high=20*len(map_palette))
map_colorbar = ColorBar(
    color_mapper= map_color_mapper,
    label_standoff=2, border_line_color=None,
    location=(0,0),
    bar_line_alpha = 0.5,
    major_label_text_align = 'left',
    )

"""
# %% Make figure
________________________________________________________________________________
"""
graph_fig = figure(
    title="(Tap on the graph to select a date, then update the map with the data for that date)",
    tools= "xpan,ypan,wheel_zoom,tap,reset,hover,save",active_tap='tap',
    #toolbar_location=plot_settings['toolbar_location'],
    x_axis_type='datetime',y_axis_type="linear",
    sizing_mode = 'scale_width',
     aspect_ratio = 3,
    visible = True,
    )
graph_lines = []
for n in range(0,len(graph_palette)):
    graph_lines.append(graph_fig.line(x='date',y='positive',color=graph_palette[n],source=source_data,legend_label="line_"+str(n)))

map_figs = {
    'Countries':[],
    'States':[],
    'Counties':[],
    }
map_mpolys={}

for k in map_figs:
    map_figs[k] = figure(
        name="fig_"+k,
        title="",
        tools= "pan,wheel_zoom,tap,reset,hover,save",active_tap='tap',
        #toolbar_location=plot_settings['toolbar_location'],
        # x_range=(-1.4e7,-7.4e6),
        # y_range=(2.88e6,6.28e6),
        match_aspect=True,
        x_axis_location=None, y_axis_location=None,
        x_axis_type="mercator", y_axis_type="mercator",
        sizing_mode = 'scale_width',
        aspect_ratio = 1.66,
        visible = True,
        )

    tile_provider = get_provider(CARTODBPOSITRON_RETINA)
    map_figs[k].add_tile(tile_provider)
    map_figs[k].grid.grid_line_color = None
    map_figs[k].x_range = DataRange1d()
    map_figs[k].y_range = DataRange1d()

    bztool = BoxZoomTool(match_aspect=True)
    map_figs[k].add_tools(bztool)
    map_figs[k].toolbar.active_drag=  None #bztool

    map_mpolys[k] =  map_figs[k].multi_polygons(
        'x', 'y', source=source_map,
        fill_color={'field': 'positiveIncreaseMAVPerMil', 'transform': map_color_mapper},
        fill_alpha=0.6,
        line_color="white",
        line_width=1,
        )

    with open(javascript_path+'map_callback.js','r') as f:
        map_callback = f.read()
    for ev in ['tap','doubletap']:
        map_figs[k].js_on_event(ev, CustomJS(args={
                                  'event':ev,
                                  'mpoly':map_mpolys[k],
                                  'ext_datafiles': ext_datafiles,
                                  'source_map': source_map,
                                  'graph_lines':graph_lines,
                                  },code=map_callback))

map_figs['States'].x_range.start = -1.4e7
map_figs['States'].x_range.end   = -7.4e6
map_figs['States'].y_range.start = 2.88e6
map_figs['States'].y_range.end   = 6.28e6

opts = [k for k in init_map.keys() if isinstance(init_map[k][0],int) or isinstance(init_map[k][0],float) ]

select = Select(title="Data Options:", value="positiveActiveMAVPerMil", options=opts)
select.js_on_change("value", CustomJS(args={
                              'mpoly':map_mpolys[k],
                              'ext_datafiles': ext_datafiles,
                              'graph_lines':graph_lines,
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
graph_fig.js_on_event('tap', CustomJS(args={
                              'mpoly':map_mpolys[k],
                              'ext_datafiles': ext_datafiles,
                              'graph_lines':graph_lines,
                              },code=graph_callback))

opts = [k for k in init_data.keys() if isinstance(init_data[k][0],int) or isinstance(init_data[k][0],float) ]

select2 = Select(title="Data Options:", value="positiveActiveMAVPerMil", options=opts)
select2.js_on_change("value", CustomJS(args={
                              'mpoly':map_mpolys[k],
                              'ext_datafiles': ext_datafiles,
                              'graph_lines':graph_lines,
                              },code="""
    console.log('select: value=' + this.value, this.toString())
    line.glyph.y.field = this.value
    line.data_source.change.emit()

"""))
"""
# %% Combine all the graphs
________________________________________________________________________________
"""

tabs = Tabs(tabs=[Panel(child=map_figs[k],title=k) for k in map_figs])

# Layout the figures and show them
# layout = column(row(select,p),row(select2,p2),
#                 sizing_mode='scale_width')
layout = column(tabs,graph_fig,sizing_mode='scale_width')
layout.margin = (4,20,4,20) # top, right, bottom, left
save(layout,template=template_ext_js(['jquary','pako']))
#view('http://localhost:7800/'+output_filename+'.html')
