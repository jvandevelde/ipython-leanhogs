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
last_year = curr_year - 1
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
    # on Jan 1st, we will always need to roll over last years data into the historical dataset
    if all(column.endswith(str(last_year)) == False for column in hist_df.columns):
        print('Loaded historical data does not include \'{0}\' (is it January?). Performing rollover...'.format(curr_year))
        last_year_df = get_leanhog_contract_data([last_year])
        util.print_df(last_year_df)
        hist_df = pd.concat([hist_df, last_year_df], axis=1)
        util.print_df(hist_df.columns)
        with open(hist_data_filename, 'wb') as fi:
            pickle.dump(hist_df, fi)

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
    
    histContractDataFile = Path(filename)

    if histContractDataFile.is_file():
        print('Loading data from file \'{0}\''.format(filename))
        contract_df = pd.read_pickle(filename)
    else:
        print('Datafile \'{0}\' does not exist. Creating...'.format(filename))
        contract_df = get_and_save_data_from_quandl(years, filename)
        
    return contract_df

def get_and_save_data_from_quandl(years, filename):
    contract_df = pd.DataFrame()

    contract_df = get_leanhog_contract_data(years)
    with open(filename, 'wb') as fi:
        pickle.dump(contract_df, fi)

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
    
    # take out any of the columns that Quandl didn't return that were expected
    # possibly a contract year that hasn't started
    columnList = [x for x in columnList if x in df.columns]
    
    df = df[columnList]
    df.rename(columns=columnRenameDict, inplace=True)
    
    return df

def get_existing_file_age(filename):
    delta = None

    dataFile = Path(filename)
    
    if dataFile.is_file():
        filetime = os.path.getmtime(filename) # filename is the path to the local file you are refreshing
        formattedTime = time.strftime('%m/%d/%Y', time.localtime(filetime))
        print("{0} was last updated on: {1}".format(filename, formattedTime))
        now = time.time()
        delta = dt.timedelta(seconds=now - filetime)
    
    return delta