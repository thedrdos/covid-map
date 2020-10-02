# Interactive Geographical Maps of COVID19 Data With Time History

Main presentation page: [https://covid-interactive-map.netlify.com](https://covid-interactive-map.netlify.com)

* Interactive geographical heat map of the rate of virus spread
* Granularity (for US, both state and county level)
* Normalization with respect to population (crude measure of societal pressure)

## Maps
* [World Map Online, full length data history](plots/map_World_PerMil.html) (small file, loads fast, but fetches data online)
* [USA Map Online, full length data history](plots/map_US_PerMil.html) (small file, loads fast, but fetches data online)
* [World/USA/County Map Online, Customizable, with history Animation, full length data history](plots/map_graph_Custom.html) (small file, loads fast, but fetches data online)
* [More mobile friendly version layout of the map above](plots/map_graph_Custom_mobile.html) (small file, loads fast, but fetches data online)
* [USA Map Online, full length data history, default 4-month view ](plots/map_4mon_external_data.html) (small file, loads fast, but fetches data online)
* [USA Map Standalone, truncated 4-month data history](plots/map_4mon_standalone.html) (large file, may take a few sec to load)

## Current Implementation

Code written in Python (and Javascript) to generate interactive html page.

The bash shell script `code/run_full_map_site_update.sh` runs all the necessary Python scripts/functions to generate the underlying data structures, maps, and html file/s.  The scripts create files in an untracked subdirectory `code/tmp_data/`  and generates a runtime performance report. Roughly:

* `match_data_and_maps.py` Updates the COVID data, loads geographical data, matches the naming and organizes in dictionaries, saves to temporary data files.
* `process_data_and_maps.py` Processes the data, calculating rates, averages, normalizations, and adding current stats to the geographical data, saves to temporary data files.
* `make_external_datafiles.py` Writes the compressed external datafiles.
* `map_4mon_external_data.py` (Legacy) Make the USA Map with state and county data history.
* `map_4mon_standalone.py` (Legacy) Make the offline version USA Map with state and county data history, truncates the data history.
* `map_US_PerMil.py` Make the USA Map with state and county population normalized COVID data history.
* `map_World_PerMil.py` Make the World Map with population normalized COVID data history.
* `map_graph_Custom.py` Make the customizable and graph, with animation function.
* `map_graph_Custom.py` Same but with the `mobile` option, with improved layout for mobile use.
* `make_website.py` Makes the acompanying website.
* Normally takes about 2-3min to run (2.2GHz Intel Core i7, 16GB 2400 DDR4)

## Sources

* Produced using Python with Bokeh and other modules
* GitHub repository for this project: [https://github.com/thedrdos/covid-map](https://github.com/thedrdos/covid-map)
* State and County Geographical Data from [The US Census Bureau](http://www2.census.gov/geo/tiger/)
* COVID-19 Data on States from [The COVID Tracking Project](https://covidtracking.com) or on [GitHub](https://github.com/COVID19Tracking/covid-tracking-data)
* COVID-19 Data on Counties from [The John Hopkins University Coronavirus Resource Center](https://coronavirus.jhu.edu)
     or on [GitHub](https://github.com/CSSEGISandData/COVID-19.gi)

## Tasklist
- [x] Implement maps using external json files for data.
- [x] Generate a cumulative USA time history graph.
- [x] Fix/Workaround bug in Bokeh where patches with multiple polygons (NaN separated) seem to draw repeatedly (alpha will be wrong)
- [x] Make a world map similar to the states map/graph.
- [x] Incorporate additional data available for states
- [x] New map plot with customizable time history data graph.
- [x] Rework the data structures generation with multithreading.
- [x] Rework the data structures for efficiency and streamlining.  
- [x] Make option to switch normalization on/off (sort of, the custom map effectively let you)
