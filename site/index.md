# Interactive Geographical Maps of COVID19 Data With Time History

Well sourced COVID19 data with the following key features:

* Interactive geographical heat map of the rate of virus spread
* Granularity (for US, both state and county level)
* Normalization with respect to population (crude measure of societal pressure)
op
## Maps
* [Animated NYT Styled Map](plots/AnimateNYT_custom_mobile.html) (faster animation implementation, based on NYT data)
* [World Map Online, full length data history](plots/map_World_PerMil.html) (small file, loads fast, but fetches data online)
* [USA Map Online, full length data history](plots/map_US_PerMil.html) (small file, loads fast, but fetches data online)
* [World/USA/County Map Online, Customizable, with history Animation, full length data history](plots/map_graph_Custom.html) (small file, loads fast, but fetches data online)
* [More mobile friendly version layout of the map above](plots/map_graph_Custom_mobile.html) (small file, loads fast, but fetches data online)
* [USA Map Online, full length data history, default 4-month view ](plots/map_4mon_external_data.html) (small file, loads fast, but fetches data online)
* [USA Map Standalone, truncated 4-month data history](plots/map_4mon_standalone.html) (large file, may take a few sec to load)

## Implementation

Code written in Python (and Javascript) to generate interactive html page.

## Sources

* Produced using Python with Bokeh and other modules
* GitHub repository for this project: [https://github.com/thedrdos/covid-map](https://github.com/thedrdos/covid-map)
* State and County Geographical Data from [The US Census Bureau](http://www2.census.gov/geo/tiger/)
* COVID-19 Data on States from [The New York Times](https://www.nytimes.com/interactive/2021/us/covid-cases.html) on [GitHub](https://github.com/nytimes/covid-19-data).
* ~~COVID-19 Data on States from [The COVID Tracking Project](https://covidtracking.com) or on [GitHub](https://github.com/COVID19Tracking/covid-tracking-data)~~ (this project has been sunset).
* COVID-19 Data on Countries and Counties from [The John Hopkins University Coronavirus Resource Center](https://coronavirus.jhu.edu) or on [GitHub](https://github.com/CSSEGISandData/COVID-19.gi)

