import pickle
import pandas as pd
import Quandl as q
from pathlib import Path
import datetime as dt
import os
import time
import sys

import utility as util

curr_year = dt.date.today().year
all_months = list(util.months.keys())

hist_data_filename = "data.hist.pickle"
hist_years = range(2000, curr_year)

data_filename = "data.pickle"
threshold = dt.timedelta(days=1)
curr_years = range(curr_year, curr_year + 2) # range(stop) param is not inclusive

all_years = range(2011, dt.date.today().year + 2) 


def load_data():
    contract_df = pd.DataFrame()
    
    # make sure we have contract data from the past (1995 to curr-1)
    hist_df = load_existing_data_file(hist_years, hist_data_filename)

    # if the file doesn't exist or is out of date, download from Quandl
    curr_df = pd.DataFrame()
    delta = get_existing_file_age(data_filename)
    if (delta is None) or (delta > threshold) :
        curr_df = get_and_save_data_from_quandl(curr_years, data_filename)
    else:
        curr_df = load_existing_data_file(curr_years, data_filename)
    
    contract_df = pd.concat([hist_df, curr_df], axis=1)
    
    return contract_df

def load_existing_data_file(years, filename):
    contract_df = pd.DataFrame()

    try:
        histContractDataFile = Path(filename)
        if histContractDataFile.is_file():
            print('Loading data from file \'{0}\''.format(filename))
            contract_df = pd.read_pickle(filename)
        else:
            print('\'{0}\' does not exist'.format(filename))
            contract_df = get_and_save_data_from_quandl(years, filename)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    
    return contract_df

def get_and_save_data_from_quandl(years, filename):
    contract_df = pd.DataFrame()

    try:
        contract_df = get_leanhog_contract_data(years)
        with open(filename, 'wb') as fi:
            pickle.dump(contract_df, fi)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    
    return contract_df

def get_leanhog_contract_data(years):
    print("Loading contracts from Quandl web service....")
    print('  loading years: {0}'.format(years))
    recordList = []
    columnList = []
    columnRenameDict = {}
    for year in years :
        for month in all_months :
            s = "CME/LN{0}{1}".format(month, year)
            recordList.append(s)
            t = "CME.LN{0}{1} - Settle".format(month, year)
            tx = "LN{0}{1}".format(month, year)
            # May contracts didn't start until 2008'
            if not ((month == 'K') and (year < 2008)): 
                columnList.append(t)
                columnRenameDict.update({t:tx})

    df = q.get(recordList,
           authtoken="dXzByDoZicZy-WFvPyTf")
    df = df[columnList]
    df.rename(columns=columnRenameDict, inplace=True)
    
    return df

def get_existing_file_age(filename):
    delta = None

    histContractDataFile = Path(filename)
    
    if histContractDataFile.is_file():
        filetime = os.path.getmtime(filename) # filename is the path to the local file you are refreshing
        print("Last save date: {0}".format(filetime))
        now = time.time()
        delta = dt.timedelta(seconds=now - filetime)
    
    return delta