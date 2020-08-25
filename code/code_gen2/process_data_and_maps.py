# Clear the Spyder console and variablestry:    from IPython import get_ipython    #get_ipython().magic('clear')    get_ipython().magic('reset -f')except:    passfrom time import time as nowfrom time import perf_counter as pnowimport pickleimport numpy as npimport pandas as pdfrom bokeh.models import ColumnDataSource # for interfacing with Pandasimport multiprocessing as mp# mp_dic = {} # will use this for multi processing as a simple passing of input dataimport progress_bar as pbarT0 = now()# %% '''------------------------------------------------------------------------------Load Data------------------------------------------------------------------------------'''print("Load Data:")t0=pnow()data_path = './tmp_data/'data = pickle.load(open(data_path+'tmp_data_and_maps.p','rb'))print("    Loading Completed in :{} sec".format(pnow()-t0))# From: (assign the keys as variables in the workspace)# data = {#     'covid_data': covid_data,#     'GraphData':GraphData,     #     'MapData':MapData,#     'Type_to_LocationNames':Type_to_LocationNames,#     'LocationName_to_Type':LocationName_to_Type,#         }for d in data:    globals()[d] = data[d]del data# %%'''------------------------------------------------------------------------------Process Data------------------------------------------------------------------------------'''print("Process Data:")t0=pnow()# Support Functionsdef diff(x):    return np.diff(x)def pdiff(x):    return np.clip(np.diff(x),0,None)def cds_to_jsonreadydata(cds,nan_code):    data = {}    for k in cds.data:        data[k] = np.nan_to_num(cds.data[k],nan=nan_code).tolist() # replace NaNs and cast to float using tolist    return data# CPT key definitions: https://covidtracking.com/about-data/data-definitions # JH only has: 'positive','death'# List of keys all will havekeys_all = ['positive',            'positiveIncrease',            'positiveIncreaseMAV',            'recovered',            'recoveredIncrease',            'recoveredIncreaseMAV',            'positiveActive',            'positiveActiveIncrease',            'positiveActiveIncreaseMAV',            'death',            'deathIncrease',            'deathIncreaseMAV10',            ]popnorm_list = keys_all     # list of keys to normalizedpopnorm_postfix = 'PerMil'  # postfix applied to normalized namesdef mp_df_processing(l):    df = covid_data[l]['dataframe'].copy()        # Remove dates with no reported cases and calculate active positive cases    df = df[df['positive']!=0]        # Fill in x day old cases as recovered if no recovery data is available    rdays = 15 # assumed number of days it takes to recovere    if df['recovered'].count()<7: # if less than one week of recovered reporting, then ignore it        df['recovered'] = 0    if df['recovered'].fillna(0).sum()==0:        stmp = df['positive']        df['recovered']=stmp.shift(rdays).fillna(0)-df['death']    df['recovered'] = df['recovered'].replace(0, float('NaN'))        # Calculate recovered increase    df['recoveredIncrease'] = df['recovered'].rolling(2).apply(pdiff)    df['recoveredIncreaseMAV'] = df['recoveredIncrease'].rolling(7).mean()        # Calculate positive active cases    df["positiveActive"] = df["positive"].fillna(0)-df["recovered"].fillna(0)-df["death"].fillna(0)        # Calculate actual and averaged increase    if 'positiveIncrease' not in df:        df['positiveIncrease'] = df['positive'].rolling(2).apply(pdiff)    df['positiveIncreaseMAV'] = df['positiveIncrease'].rolling(7).mean()    df['positiveActiveIncrease'] = df['positiveActive'].rolling(2).apply(diff)    # Remove active calculations from when recovered data was not available, and one more entry to avoid the resultant cliff    if len(df['positive'].values)>1:        df.loc[df['recovered'].isnull(),'positiveActiveIncrease'] = float('NaN')        try:            df.loc[df['positiveActiveIncrease'].first_valid_index(),'positiveActiveIncrease']=float('NaN')        except:            pass    df['positiveActiveIncreaseMAV'] = df['positiveActiveIncrease'].rolling(7).mean()    if len(df['positive'].values)>1:        df.loc[df['recovered'].isnull(),'positiveActiveIncrease'] = float('NaN')            # Calculate deaths    if 'deathIncrease' not in df:        df['deathIncrease'] = df['death'].rolling(2).apply(diff)    df['deathIncreaseMAV10'] = df['deathIncrease'].rolling(7).mean()*10        # Normalize wrt population    if covid_data[l]['population']>0:        pnorm = 1000000/covid_data[l]['population']    else:        pnorm = np.nan            for k in popnorm_list:        df[k+popnorm_postfix] = df[k]*pnorm            # Convert dataframe to ColumnDataSource    cds = ColumnDataSource(df)    # Convert the data in the ColumnDataSource to encoded float arrays ready to be json        out = {        'l':l,        'data': cds_to_jsonreadydata(cds,GraphData[l]['nan_code'])}    return out  # N = len(GraphData)# for n,l in enumerate(GraphData):#     # mp_df_processing(l)#     if n%10==0:#         pbar.progress_bar(n,N-1)# pbar.progress_bar(n,N-1)        # Use multi processing to process the dataframesN = len(GraphData)Ncpu = min([mp.cpu_count(),N]) # use maximal number of local CPUschunksize = 1pool = mp.Pool(processes=Ncpu)for n,d in enumerate(pool.imap_unordered(mp_df_processing,GraphData.keys(),chunksize=chunksize)):    #pbar.progress_bar(n,-(-N/chunksize)-1)    #pbar.progress_bar(n,N-1)    GraphData[d['l']]['data'] = d['data']    if n%15==0:        pbar.progress_bar(n,N-1)    passpbar.progress_bar(n,N-1)pool.terminate()print("    Completed in :{} sec".format(pnow()-t0))print("Pickling COVID Data and Maps After Matching:")t0=pnow()data_path = './tmp_data/'data = {    'covid_data': covid_data,    'GraphData':GraphData,         'MapData':MapData,    'Type_to_LocationNames':Type_to_LocationNames,    'LocationName_to_Type':LocationName_to_Type,        }pickle.dump(data,open(data_path+'tmp_data_and_maps.p','wb'))print("    Completed in :{} sec".format(pnow()-t0))t0=pnow()print("Script Completed in :{} sec".format(now()-T0))