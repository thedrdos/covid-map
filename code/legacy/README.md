## Legacy Implementation

Code written in Python (and Javascript) to generate interactive html page.

The bash shell script `code/run_full_map_site_update.sh` runs all the necessary Python scripts/functions to generate the underlying data structures and maps html file/s.  The scripts create files in an untracked subdirectory `code/tmp_data/`. Roughly:

* `get_data_for_maps.py` Updates the COVID data, loads it and loads the geographical data, saving to temporary data files.
* `process_data_for_maps.py`  Processes the data, calculating rates, averages, normalizations, and adding current stats to the geographical data, saving to temporary data files.
* `python map_4mon_standalone.py` Makes the USA Map Standalone with 4-months of data history from the processed data.
* `make_website.py` Makes the acompanying website (tied/synced from [Netlify](www.netlify.com) directly to [Github](www.github.com))
* Normally takes about 5min to run (2.2GHz Intel Core i7, 16GB 2400 DDR4)
