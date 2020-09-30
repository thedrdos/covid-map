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
from bokeh.models import ColorBar, ColorMapper, LogColorMapper, LogTicker, LinearColorMapper, NumeralTickFormatter
from bokeh.models import BasicTicker as LinearTicker
from bokeh.models import BasicTickFormatter, LogTicker, FixedTicker, FuncTickFormatter
from bokeh.palettes import Magma11 as palette
from bokeh.palettes import Inferno256, Turbo256
from bokeh.plotting import figure
from bokeh.models import Div
from bokeh.models import ColumnDataSource, DateRangeSlider, Select
from bokeh.models.tools import HoverTool, BoxZoomTool  # for showing the hover tool

from bokeh_template_external_js import template as template_ext_js

from bokeh import events
from bokeh.models import Label, LabelSet, CustomJS, TapTool, Toggle, Button, Spacer, TextInput, RadioButtonGroup
from bokeh.tile_providers import CARTODBPOSITRON_RETINA, get_provider
import os

import numpy as np
import datetime
from datetime import date, timedelta

from bokeh.models import NumeralTickFormatter, BasicTickFormatter
# for adding the second axis
from bokeh.models import LogAxis, LinearAxis, Range1d, DataRange1d
# for formatting the dates on the x axis
from bokeh.models import DatetimeTickFormatter

from bokeh.layouts import column, row, gridplot, layout  # For show multiple figures


# For adding spans (vertical/horizontal lines without end points)
from bokeh.models import Span

import pandas as pd

import pickle
import progress_bar as pbar

import json
import gzip

import sys

"""
# Assign output file
________________________________________________________________________________
"""


def filename(fullname):
    """ Return the name of a file without its path or extension"""
    return os.path.splitext(os.path.split(fullname)[1])[0]


this_filename = filename(os.path.basename(os.path.splitext(__file__)[0]))
javascript_path = './' + this_filename + '_js/'
localhost_path = './plots/'
# name the output file/s after the script file
output_filename = "./../site/plots/" + this_filename
output_file(output_filename + ".html",
            title="Interactive Map of USA COVID19 Data with Time History")  # title=filename(output_filename))

"""
# Support functions
________________________________________________________________________________
"""


def dic_nan_decode(d, nan_code):
    for k in d:
        d[k] = array_element_replace(d[k], nan_code, float('NaN'))
    return d


def array_element_replace(arr, old_value, new_value):
    for i in range(0, len(arr)):
        if isinstance(arr[i], list):
            arr[i] = array_element_replace(arr[i], old_value, new_value)
        else:
            if arr[i] == old_value:
                arr[i] = new_value
    return arr


"""
# Load key_to_filename
________________________________________________________________________________
"""
ext_datafiles = {
    'path': "../site/plots/data/",
    'rel_path': "./data/",
}
with gzip.GzipFile(ext_datafiles['path'] + 'filename_to_location.json.gz', 'r') as fin:
    ext_datafiles['filename_to_location'] = json.loads(
        fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path'] + 'location_to_filename.json.gz', 'r') as fin:
    ext_datafiles['location_to_filename'] = json.loads(
        fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path'] + 'location_to_mapfilename.json.gz', 'r') as fin:
    ext_datafiles['location_to_mapfilename'] = json.loads(
        fin.read().decode('utf-8'))


"""
# %% Load json file for initiallization
________________________________________________________________________________
"""
init_location = 'New York, US'  # get location
with gzip.GzipFile(ext_datafiles['path'] + ext_datafiles['location_to_filename'][init_location] + '.json.gz', 'r') as fin:
    init_datafile = json.loads(fin.read().decode('utf-8'))
init_data = dic_nan_decode(init_datafile['data'], init_datafile['nan_code'])
init_data['date'] = pd.to_datetime(init_data['date'])
latest_data_date = max(init_data['date'])
oldest_date_date = min(init_data['date'])

init_location = 'Earth'  # get location
with gzip.GzipFile(ext_datafiles['path'] + ext_datafiles['location_to_filename'][init_location] + '_map.json.gz', 'r') as fin:
    init_mapfile = json.loads(fin.read().decode('utf-8'))
init_map = init_mapfile['data']

# Create source data structure and initialize state map
source_graph = ColumnDataSource(init_data)
source_map = ColumnDataSource(init_map)
# Erase the underlying data to reduce the html filesize (will be loaded upon user tap feedback)
source_graph.data = {k: source_graph.data[k][-2:-1] for k in source_graph.data}

"""
# %% Make State graph for COVID data
________________________________________________________________________________
"""
# Set Soft Axis limits
ax_limits = {
    'x': (
        pd.Timestamp.now() - pd.DateOffset(months=4),
        pd.Timestamp.now()
    ),
}
# Create figure
p_graph = figure(x_axis_type='datetime', y_axis_type="linear",
                 title='(Tap a state on the map above to show the corresponding COVID data here)',
                 # plot_width=800, plot_height=600,
                 tools="ypan,xpan,ywheel_zoom,xwheel_zoom,ybox_zoom,xbox_zoom,box_zoom,reset", active_scroll=None, active_drag='ypan',
                 toolbar_location='left',
                 sizing_mode='scale_width',
                 aspect_ratio=2,
                 visible=True,
                 y_axis_location='right',
                 )  # Assign tools and make wheel_zoom default on

# Make the bar and line plots
glyphs = []
graph_init = {
    'x': 'date',
    'source':   source_graph,
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
    'line_color': [
        'red',  # mapper,
        'yellowgreen',  # color_mapper,
        'blue'],
    'line_width': [
        4, 4, 4
    ],
    'line_dash': [
        'solid', 'solid', 'solid'],
    'name': ['' for i in range(0, 3)],
}
for n, y in enumerate(graph_init['y']):
    graph_init['name'][n] = y

for n, y in enumerate(graph_init['y']):
    glyphs.append(
        p_graph.line(
            source=graph_init['source'],
            x=graph_init['x'],
            y=graph_init['y'][n],
            # legend_label=graph_init['legend_label'][n],
            line_color=graph_init['line_color'][n],
            color=graph_init['line_color'][n],
            line_width=graph_init['line_width'][n],
            line_dash=graph_init['line_dash'][n],
            name=graph_init['name'][n],
        )
    )
p_graph.yaxis[0].formatter = NumeralTickFormatter(format="0,0.0")

# Horizontal right axis zero span
zero_span = Span(
    location=0,  # Span the 0 line of the right y axis
    dimension='width', line_color='gray',
    line_dash='solid', line_width=3, line_alpha=0.4,
)
p_graph.add_layout(zero_span)

# Weekly span marks
duration = np.timedelta64(4, 'm')
ds = np.arange(ax_limits['x'][0], ax_limits['x'][1], dtype='datetime64[D]')
# use of timezones was depricated, before timezone=None was needed
day = np.timedelta64(1, 'D')
for d in ds:
    if ((np.timedelta64(ds.max() - d) / day) % 7) == 0:
        ts = (np.datetime64(d) - np.datetime64('1970-01-01T00:00:00')) / \
            np.timedelta64(1, 's')
        wloc = ts * 1000  # get the week mark location in a format compatible with annotations
        p_graph.add_layout(
            Span(location=wloc,
                 dimension='height', line_color='gray',
                 line_dash='dashed', line_width=2, line_alpha=0.5,
                 ))


# # X axis formatting:
p_graph.x_range = Range1d(ax_limits['x'][0], ax_limits['x'][1])
p_graph.xaxis.major_label_orientation = -np.pi / 3  # slant the labels
dtformat = "%b-%d"
p_graph.xaxis.formatter = formatter = DatetimeTickFormatter(  # Always show the same date formatting regardless of zoom
    days=dtformat,
    months=dtformat,
    hours=dtformat,
    minutes=dtformat)

# Add legend
#p_graph.legend.location = "top_left"

# Add a hover tool
hover = HoverTool()
hover.tooltips = [
    #('Type', "$name"),
    ('', '$name: @$name{0,0.} on @date{%a-%b-%d}'),
]
# hover.mode = 'vline'
hover.formatters = {
    '@date': 'datetime',  # use 'datetime' formatter for '@date' field
    '$name': 'printf'  # use 'printf' formatter for the name of the column
}
hover.renderers = glyphs
p_graph.add_tools(hover)

p_graph_glyphs = glyphs

"""
%% Setup color map
________________________________________________________________________________
"""
palette = Turbo256[128:-1:5]
color_mapper = LinearColorMapper(
    palette=palette, low=0, high=20 * len(palette))

color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=2, border_line_color=None, location=(0, 0),
    bar_line_alpha=0.5,
    major_label_text_align='left',
)

"""
# Make the map
________________________________________________________________________________
"""
p_map = figure(
    title=latest_data_date.strftime('%Y-%m-%d'),
    # x_range=minmax(DS_worlds_map.data['xc']), y_range=minmax(DS_worlds_map.data['yc']),
    # x_range=(-1.4e7,-7.4e6),
    # y_range=(2.88e6,6.28e6),
    # sizing_mode='stretch_width',
    tools="tap,pan,wheel_zoom,reset,save", active_tap='tap',
    toolbar_location='left',
    x_axis_location=None, y_axis_location=None,
    x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode='scale_width',
    aspect_ratio=2,
    match_aspect=True,
)
p_map.grid.grid_line_color = None
bztool_s = BoxZoomTool(match_aspect=True)
p_map.add_tools(bztool_s)
p_map.toolbar.active_drag = None  # bztool_s

# Add the map tiles
tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p_map.add_tile(tile_provider)

# Add the states1
p_map_mpoly = p_map.multi_polygons(
    xs='x', ys='y', source=source_map,
    fill_color={'field': 'positiveIncreaseMAVPerMil',
                'transform': color_mapper},
    fill_alpha=0.6,
    line_color="white",
    line_width=1,
)
p_map.add_layout(color_bar, 'right')
# Add the hover tool to show the state name and number of counties
hoverm = HoverTool()
hoverm.tooltips = [
    ('Name', "@name"),
    ("Population", "@population{0,0.}"),
    #("Current COVID Statistics","{}".format('-'*15)),
    ('Positive Cases', "@positive{0,0.}"),
    ('Recovered Cases', "@recovered{0,0.}"),
    ('Positive Active Cases', "@positiveActive{0,0.}"),
    ('Deaths', "@death{0,0.}"),
]
p_map.add_tools(hoverm)

# Add taptool to select from which state to show all the counties
with open(javascript_path + 'callback_map.js', 'r') as f:
    callback_world_map = f.read()
callbacktap = CustomJS(args={'ext_datafiles': ext_datafiles,
                             'p_graph_glyphs': p_graph_glyphs,
                             'p_graph': p_graph,
                             },
                       code=callback_world_map)
taptool = p_map.select(type=TapTool)
taptool.callback = callbacktap

# Explicitly initialize x range
p_map.x_range = DataRange1d()

# %% Make data graphs reset on doubletap
p_graph.js_on_event('doubletap', CustomJS(args={'p': p_graph, }, code="""
    p.reset.emit()
    """))

"""
# Map widgets
------------------------------------------------------------------------------------------------
"""
# Get the callback script used for many of the widgets
with open(javascript_path + 'callback_map_widgets.js', 'r') as f:
    callback_widgets = f.read()

# Level radio buttons
radio_labels = ["Play \u25B6", "Step \u23ef", "Pause \u23f8"]
radioGroup_play_controls = RadioButtonGroup(
    labels=radio_labels, active=2, name='radioGroup_play_controls')
radioGroup_play_controls.js_on_click(CustomJS(args={
            'event': 'radioGroup_play_controls',
            'ext_datafiles': ext_datafiles,
            'mpoly': p_map_mpoly,
            'source_map': source_map,
            'p_map': p_map,
             },
    code=callback_widgets))

# %% Make date range slider
date_range_slider = DateRangeSlider(value=((latest_data_date), (latest_data_date)),
                                    start=(oldest_date_date), end=(latest_data_date),
                                    name='date_range_slider')
date_range_slider.js_on_change("value", CustomJS(args={
            'event': 'date_range_slider',
            'ext_datafiles': ext_datafiles,
            'mpoly': p_map_mpoly,
            'source_map': source_map,
            'p_map': p_map,
},
    code=callback_widgets
))


# Level radio buttons
radio_labels = ["World Level", "States Level", "Counties Level"]
radioGroup_level_select = RadioButtonGroup(
    labels=radio_labels, active=0, name='radioGroup_level_select')
radioGroup_level_select.js_on_click(CustomJS(args={
             'event': 'level_select',
             'mpoly': p_map_mpoly,
             'ext_datafiles': ext_datafiles,
             'source_map': source_map,
             'p_map': p_map,
},
    code=callback_widgets))

#
continental_states = [
    'Alabama, US', 'Arizona, US', 'Arkansas, US', 'California, US', 'Colorado, US', 'Connecticut, US', 'Delaware, US', 'District of Columbia, US', 'Florida, US', 'Georgia, US', 'Idaho, US', 'Illinois, US', 'Indiana, US', 'Iowa, US', 'Kansas, US', 'Kentucky, US', 'Louisiana, US', 'Maine, US', 'Maryland, US', 'Massachusetts, US', 'Michigan, US', 'Minnesota, US', 'Mississippi, US', 'Missouri, US', 'Montana, US', 'Nebraska, US', 'Nevada, US', 'New Hampshire, US', 'New Jersey, US', 'New Mexico, US', 'New York, US', 'North Carolina, US', 'North Dakota, US', 'Ohio, US', 'Oklahoma, US', 'Oregon, US', 'Pennsylvania, US', 'Rhode Island, US', 'South Carolina, US', 'South Dakota, US', 'Tennessee, US', 'Texas, US', 'Utah, US', 'Vermont, US', 'Virginia, US', 'Washington, US', 'West Virginia, US', 'Wisconsin, US', 'Wyoming, US']

button_continental_us_only = Toggle(label="Continental US Only",
                                    visible=True,
                                    button_type='default',
                                    name='button_continental_us_only')
button_continental_us_only.js_on_change('active', CustomJS(args={
    'event':'button_continental_us_only',
    'mpoly': p_map_mpoly,
    'ext_datafiles': ext_datafiles,
    'source_map': source_map,
    'p_map': p_map,
    'continental_states': continental_states,
}, code=callback_widgets))

# Selectors for the map
selectors_map = []
opts = [k for k in init_data.keys() if isinstance(init_data[k][0], int)
        or isinstance(init_data[k][0], float)]
opts = sorted(opts)
select = Select(title="Data For Map Coloring:",
                value=p_map_mpoly.glyph.fill_color['field'],
                options=opts)
select.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'mpoly': p_map_mpoly,
}, code="""
        //console.log('select: value=' + this.value, this.toString())
        mpoly.glyph.fill_color.field = this.value
        mpoly.data_source.change.emit()
    """))
selectors_map.append(select)

# Range setting for map
map_range_widgets = []
text_input = TextInput(value=str(color_mapper.low), title="Low Color")
text_input.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'color_mapper': color_mapper,
}, code="""
     color_mapper.low = Number(this.value)
"""))
map_range_widgets.append(text_input)
text_input = TextInput(value=str(color_mapper.high), title="High Color")
text_input.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'color_mapper': color_mapper,
}, code="""
    color_mapper.high = Number(this.value)
"""))
map_range_widgets.append(text_input)

"""
# Line graph widgets
------------------------------------------------------------------------------------------------
"""
# Selectors for the line graphs
selectors_graph = []
opts = [k for k in init_data.keys() if isinstance(init_data[k][0], int)
        or isinstance(init_data[k][0], float)]
opts = sorted(opts)
for n, g in enumerate(p_graph_glyphs):
    select = Select(title=" ",  # title="Data For Line "+str(n+1)+":",
                    value=g.glyph.y,
                    options=opts,
                    background=g.glyph.line_color,)
    select.js_on_change("value", CustomJS(args={
        'ext_datafiles': ext_datafiles,
        'line': g,
    }, code="""
        //console.log('select: value=' + this.value, this.toString())
        line.glyph.y.field = this.value
        line.data_source.change.emit()
    """))
    selectors_graph.append(select)

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
    data_update=pd.to_datetime(latest_data_date).strftime('%Y-%m-%d'),
    graph_update=pd.Timestamp.now().strftime('%Y-%m-%d'),
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
p_map.sizing_mode = 'scale_width'
p_graph.sizing_mode = 'scale_width'
# layout = column(heading,
#                 row(p_map, sizing_mode='scale_width'),
#                 row(date_range_slider, sizing_mode='scale_width'),
#                 row(column(selectors_graph[0],selectors_graph[1],selectors_graph[2],width=250,sizing_mode="scale_height"),p_graph, sizing_mode='scale_width'),
#                 row(footer, sizing_mode='scale_width'),
#                 sizing_mode='scale_width')
# lout = layout([heading,
#     [selectors_map+map_range_widgets+[play_button],p_map],
#     date_range_slider,
#     [selectors_graph,p_graph],
#     footer
#     ])
lout = layout([heading,
               [selectors_map + map_range_widgets + [radioGroup_level_select] +
                   [button_continental_us_only], p_map],
               [radioGroup_play_controls, date_range_slider],
               [selectors_graph, p_graph],
               footer
               ])
lout.margin = (4, 20, 4, 20)  # top, right, bottom, left
lout.sizing_mode = 'scale_width'
save(lout, template=template_ext_js(['jquary', 'pako']))
# view(output_filename+'.html')
# view('http://localhost:7800/'+localhost_path+this_filename+'.html')
