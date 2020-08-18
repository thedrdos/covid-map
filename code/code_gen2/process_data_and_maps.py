import get_maps as gmimport get_data as gdimport picklefrom time import time as nowfrom time import perf_counter as pnowimport re# For multi processingimport multiprocessing as mpmp_dic = {} # will use this for multi processing as a simple passing of input data# %% Load dataprint("Get COVID Data names:")t0=pnow();country_dnames = gd.get_countries()state_dnames   = gd.get_states()county_dnames  = gd.get_counties()print("Completed in :{} sec".format(pnow()-t0))t0=pnow();print("Get COVID Data:")country_data = gd.load(country_dnames)county_data  = gd.load(county_dnames)state_data   = gd.load(state_dnames)print("Completed in :{} sec".format(pnow()-t0))t0=pnow();print("Get Maps:")country_maps = gm.get_maps('country')county_maps  = gm.get_maps('county')state_maps   = gm.get_maps('state')print("Completed in :{} sec".format(pnow()-t0))t0=pnow()# print("Pickling COVID Data and Maps:")# data_path = './tmp_data/'# pickle.dump([#     country_data,#     state_data,#     county_data,#     country_maps,#     state_maps,#     county_maps],open(data_path+'tmp_save_vars.p','wb'))# print("Completed in :{} sec".format(pnow()-t0))# t0=pnow()# print("UnPickling COVID Data and Maps:")# data_path = './tmp_data/'# country_data, state_data, county_data, country_maps, state_maps, county_maps = pickle.load(open(data_path+'tmp_save_vars.p','rb'))# print("Completed in :{} sec".format(pnow()-t0))# t0=pnow()# %% '''------------------------------------------------------------------------------Assign name for the column used for names matching the COVID data conviention------------------------------------------------------------------------------'''name_covid_data = 'NAME_COVID_DATA'# %%'''------------------------------------------------------------------------------Pre-process Country Map Data - to match with COVID data naming------------------------------------------------------------------------------'''print("Pre-processing Country Maps:")t0 = pnow();# Following list was generated by manually searching through non overlapping datatranslate_names_covid_to_map = {     'Korea, South': 'South Korea',     'US': 'United States of America',     'China': "People's Republic of China",     'Taiwan*': 'Taiwan',     'Czechia': 'Czech Republic',     'Eswatini': 'eSwatini',     'Gambia': 'The Gambia',     'North Macedonia': 'Republic of Macedonia',     'Timor-Leste': 'East Timor',     'West Bank and Gaza': 'Palestine',     'Burma': 'Myanmar',     'Holy See': 'Vatican',     "Cote d'Ivoire": "Côte d'Ivoire",     'Sao Tome and Principe':  'São Tomé and Principe',     'Congo (Kinshasa)':'Congo', # 'Congo (Brazzaville)' Covid data is also available, but the map only has one Congo, and (Kinshasa) is much larger     }# List of name columns to search through map names to match with COVID data namescheck_names = ['NAME', 'NAME_EN']# Initialize naming for COVID Data lookupcountry_maps[name_covid_data] = '' for c in country_dnames:    if c in translate_names_covid_to_map:        n = translate_names_covid_to_map[c]    else:        n = c    for k in check_names:        if n in country_maps[k].tolist():            country_maps.loc[country_maps[k]==n,name_covid_data]=c# Prune the country list to only those in both datasets, maps and COVID datacountry_names = [c for c in country_dnames if c in country_maps[name_covid_data].tolist() ]# Now the variable: country_names has a list of all the names of countries# that can be matched with both map and covid data:# for any c in country_names , then both the covid data and map geometry exist in: # country_data[c]# country_maps.loc[country_maps['NAME_COVID_DATA']==c]['geometry'].iloc[0] # %%print("Completed in :{} sec".format(pnow()-t0))'''------------------------------------------------------------------------------Pre-process State Map Data - to match with COVID data naming------------------------------------------------------------------------------'''print("Pre-processing State Maps:")t0 = pnow();translate_names_covid_to_map = {    'District Of Columbia, US': 'District of Columbia',    'US Virgin Islands, US': 'United States Virgin Islands',    'Northern Mariana Islands, US': 'Commonwealth of the Northern Mariana Islands',    }state_maps[name_covid_data] = ''for s in state_dnames:    if s in translate_names_covid_to_map:        n = translate_names_covid_to_map[s]    else:        n = s[:-4] # remove ', US'       if n in state_maps['NAME'].tolist():        state_maps.loc[state_maps['NAME']==n,name_covid_data]=sstate_names = [s for s in state_dnames if s in state_maps[name_covid_data].tolist()]print("Completed in :{} sec".format(pnow()-t0))# %%'''------------------------------------------------------------------------------Pre-process County Map And COVID Data - to match with COVID data naming------------------------------------------------------------------------------'''print("Pre-processing County Maps:")t0 = pnow();county_dnames = []for k in county_data:    knew = re.sub(r'\s*,\s*',', ',k)    knew = re.sub(r', US(, US)+',', US',knew)    if k!=knew:        county_data[knew] = county_data.pop(k)    county_dnames.append(knew)county_dnames = list(set(county_dnames)) # use only unique county full names (county, state, US)print("Step 1 in :{} sec".format(pnow()-t0))# Match state id with state namestate_name_to_state_id = {k:v for (k,v) in zip(state_maps[name_covid_data],state_maps['STATEFP'])}county_maps['NAME_STATE'] = ''for s, sid in zip(state_name_to_state_id.keys(),state_name_to_state_id.values()):    county_maps.loc[county_maps['STATEFP']==sid,'NAME_STATE'] = scounty_maps['NAME_FULL'] = ''for c, ind in zip(county_maps['NAME'],county_maps.index.tolist()):    county_maps.at[ind,'NAME_FULL'] = county_maps.at[ind,'NAME'].rstrip(' ').lstrip(' ')+', '+county_maps.at[ind,'NAME_STATE']    print("Step 2 in :{} sec".format(pnow()-t0))   translate_names_covid_to_map = {     'District of Columbia, District of Columbia, US': 'District of Columbia, District Of Columbia, US',     # 'Baltimore City, Maryland, US': ,     # 'Dukes and Nantucket, Massachusetts, US': ,     # 'Federal Correctional Institution (FCI), Michigan, US': ,     # 'Michigan Department of Corrections (MDOC), Michigan, US': ,     # 'Kansas City, Missouri, US': ,     # 'St. Louis City, Missouri, US': ,     'Dona Ana, New Mexico, US': 'Doña Ana, New Mexico, US',     'New York City, New York, US': 'New York, New York, US',     'Anasco, Puerto Rico, US': 'Añasco, Puerto Rico, US',     'Bayamon, Puerto Rico, US': 'Bayamón, Puerto Rico, US',     'Canovanas, Puerto Rico, US': 'Canóvanas, Puerto Rico, US',     'Catano, Puerto Rico, US': 'Cataño, Puerto Rico, US',     'Comerio, Puerto Rico, US': 'Comerío, Puerto Rico, US',     'Guanica, Puerto Rico, US': 'Guánica, Puerto Rico, US',     'Juana Diaz, Puerto Rico, US': 'Juana Díaz, Puerto Rico, US' ,     'Las Marias, Puerto Rico, US': 'Las Marías, Puerto Rico, US',     'Loiza, Puerto Rico, US': 'Loíza, Puerto Rico, US',     'Manati, Puerto Rico, US':'Manatí, Puerto Rico, US' ,     'Mayaguez, Puerto Rico, US': 'Mayagüez, Puerto Rico, US',     'Penuelas, Puerto Rico, US': 'Peñuelas, Puerto Rico, US',     'Rincon, Puerto Rico, US': 'Rincón, Puerto Rico, US',     'Rio Grande, Puerto Rico, US': 'Río Grande, Puerto Rico, US',     'San German, Puerto Rico, US': 'San Germán, Puerto Rico, US',     'San Sebastian, Puerto Rico, US': 'San Sebastián, Puerto Rico, US',     # 'Bear River, Utah, US': ,    # I couldn't find these on the list of Utah mapped counties     # 'Central Utah, Utah, US': ,     # 'Southeast Utah, Utah, US': ,     # 'Southwest Utah, Utah, US': ,     # 'TriCounty, Utah, US': ,     'Weber-Morgan, Utah, US': 'Weber, Utah, US',     # 'Fairfax City, Virginia, US': , # maps dont uniquesly distinguish the city boundaries (I think they are there tho)     # 'Franklin City, Virginia, US': ,     # 'Richmond City, Virginia, US': ,     # 'Roanoke City, Virginia, US': ,     # 'District of Columbia, District of Columbia, US': ,     # 'Dukes and Nantucket, Massachusetts, US': ,     # 'Kansas City, Missouri, US':  # Not given in the maps    }# county_maps[name_covid_data] = ''# for c in county_dnames:#     if c in translate_names_covid_to_map:#         n = translate_names_covid_to_map[c]#     else:#         n = c#     if n in county_maps['NAME_FULL'].tolist():#         county_maps.loc[county_maps['NAME_FULL']==n,name_covid_data]=c# Multiprocessing code that's actually a bit slower# county_maps[name_covid_data] = ''        # mp_dic = {#     'county_maps': county_maps,#     'name_covid_data': name_covid_data,#     'translate_names_covid_to_map':translate_names_covid_to_map,#     }     # def mp_name_county_maps(c):#     if c in mp_dic['translate_names_covid_to_map']:#         n = mp_dic['translate_names_covid_to_map'][c]#     else:#         n = c        #     if n in mp_dic['county_maps']['NAME_FULL'].tolist():#         out={#             'c': c,#             'n': n,#             'name':c}#     else:#         out={#             'c': c,#             'n': n,#             'name':''}      #     return out# Nitems = len(county_dnames)# Ncpu = min([mp.cpu_count(),Nitems]) # use maximal number of local CPUs# chunksize = 1# pool = mp.Pool(processes=Ncpu)# for n,d in enumerate(pool.imap_unordered(mp_name_county_maps,county_dnames,chunksize=chunksize)):#     county_maps.loc[county_maps['NAME_FULL']==d['n'],name_covid_data]=d['name']# pool.terminate()   # Much faster methodctlist = [translate_names_covid_to_map[c] if c in translate_names_covid_to_map.keys() else c for c in county_dnames] # translated listcodict = dict(zip(ctlist,county_dnames)) #{k:v for (k,v) in zip(ctlist,country_dnames)} # dict to translate the translated list back to county_dnamescounty_maps[name_covid_data] = [codict[c] if c in ctlist else '' for c in county_maps['NAME_FULL'].tolist()]county_names = [s for s in county_dnames if s in county_maps[name_covid_data].tolist()]# The counties with covid data but no map assigned:county_maps_missing = sorted([c for c in county_dnames if c not in county_names and 'Out of' not in c and 'Unassig' not in c]) print("Completed in :{} sec".format(pnow()-t0))# %%'''------------------------------------------------------------------------------Pre-process County Map And COVID Data - to match with COVID data naming------------------------------------------------------------------------------'''