# Interactive Geographical Maps of COVID19 Data With Time History

Main presentation page: [https://covid-interactive-map.netlify.com](https://covid-interactive-map.netlify.com)

* Interactive geographical heat map of the rate of virus spread
* Granularity (for US, both state and county level)
* Normalization with respect to population (crude measure of societal pressure)

## Maps
* [USA Map Online 4-month of data history](plots/map_4mon_external_data.html) (small file, loads fast, but fetches data online)
* [USA Map Standalone with 4-months of data history](plots/map_4mon_standalone.html) (large file, may take a few sec to load)

## Implementation

Code written in Python (and Javascript) to generate interactive html page.

The bash shell script `code/run_full_map_site_update.sh` runs all the necessary Python scripts/functions to generate the underlying data structures and maps html file/s.  The scripts create files in an untracked subdirectory `code/tmp_data/`. Roughly:

* `get_data_for_maps.py` Updates the COVID data, loads it and loads the geographical data, saving to temporary data files.
* `process_data_for_maps.py`  Processes the data, calculating rates, averages, normalizations, and adding current stats to the geographical data, saving to temporary data files.
* `python map_4mon_standalone.py` Makes the USA Map Standalone with 4-months of data history from the processed data.
* `make_website.py` Makes the acompanying website (tied/synced from [Netlify](www.netlify.com) directly to [Github](www.github.com))
* Normally takes about 5min to run (2.2GHz Intel Core i7, 16GB 2400 DDR4)


## Sources

* Produced using Python with Bokeh and other modules
* GitHub repository for this project: [https://github.com/thedrdos/covid-map](https://github.com/thedrdos/covid-map)
* State and County Geographical Data from [The US Census Bureau](http://www2.census.gov/geo/tiger/)
* COVID-19 Data on States from [The COVID Tracking Project](https://covidtracking.com) or on [GitHub](https://github.com/COVID19Tracking/covid-tracking-data)
* COVID-19 Data on Counties from [The John Hopkins University Coronavirus Resource Center](https://coronavirus.jhu.edu)
     or on [GitHub](https://github.com/CSSEGISandData/COVID-19.gi)

## Tasklist
- [x] Implement maps using external json files for data.
- [ ] Generate a cumulative USA time history graph.
- [ ] Fix/Workaround bug in Bokeh where patches with multiple polygons (NaN separated) seem to draw repeatedly (alpha will be wrong)
- [ ] Make a world map similar to the states map/graph.
- [ ] Incorporate additional data available for states
- [ ] New map plot with customizable time history data graph.
- [ ] Rework the data structures generation with multithreading.
- [ ] Rework the data structures for efficiency and streamlining.  
