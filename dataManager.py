import pickle
import pandas as pd
import Quandl as q
from pathlib import Path
import datetime as dt
import os
import time

import utility as util

data_filename = "data.pickle"
run_date_filename = "rundate.pickle"
all_years = range(2011, dt.date.today().year + 2) # range 'stop' - goes up to but not including
all_months = list(util.months.keys())

#df = lhdata.get_online_lh_data(allYears, months)
#df.to_pickle('data.pickle')
def load_data():
    contract_df = pd.DataFrame()

    histContractDataFile = Path(data_filename)
    delta = None
    if histContractDataFile.is_file():
        threshold = dt.timedelta(days=1) # can also be minutes, seconds, etc.
        filetime = os.path.getmtime(data_filename) # filename is the path to the local file you are refreshing
        print("Last save date: {0}".format(filetime))
        now = time.time()
        delta = dt.timedelta(seconds=now - filetime)
    if (delta is None) or (delta > threshold) :
        contract_df = get_leanhog_contract_data()
        with open(data_filename, 'wb') as fi:
            pickle.dump(contract_df, fi)
    else:
        histContractDataFile = Path(data_filename)
        if histContractDataFile.is_file():
            print("Loading from disk")
            contract_df = pd.read_pickle(data_filename)
        else:
            contract_df = get_leanhog_contract_data()
            with open(data_filename, 'wb') as fi:
                # dump your data into the file
                pickle.dump(contract_df, fi)
    
    #print('loaded columns {0}'.format(contract_df.columns))
    return contract_df


def get_leanhog_contract_data():
    print("Loading from Quandl")
    recordList = []
    columnList = []
    columnRenameDict = {}
    for year in all_years :
        for month in all_months :
            s = "CME/LN{0}{1}".format(month, year)
            recordList.append(s)
            t = "CME.LN{0}{1} - Settle".format(month, year)
            tx = "LN{0}{1}".format(month, year)
            columnList.append(t)
            columnRenameDict.update({t:tx})

    df = q.get(
        recordList, 
        authtoken= "dXzByDoZicZy-WFvPyTf")[
            columnList]

    df.rename(columns=columnRenameDict, inplace=True)
    
    return df