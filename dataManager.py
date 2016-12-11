import pickle
import pandas as pd
import Quandl as q
from pathlib import Path
import datetime as dt
import os
import time
import sys

import utility as util

data_filename = "data.pickle"
run_date_filename = "rundate.pickle"
threshold = dt.timedelta(days=1)
all_years = range(2011, dt.date.today().year + 2) # range 'stop' - goes up to but not including
all_months = list(util.months.keys())

def load_data():
    contract_df = pd.DataFrame()
    delta = get_existing_file_age()
    
    # if the file doesn't exist or is out of date, download from Quandl
    if (delta is None) or (delta > threshold) :
        contract_df = get_and_save_data_from_quandl()
    else:
        contract_df = load_existing_data_file()

    return contract_df

def get_existing_file_age():
    delta = None

    histContractDataFile = Path(data_filename)
    
    if histContractDataFile.is_file():
        filetime = os.path.getmtime(data_filename) # filename is the path to the local file you are refreshing
        print("Last save date: {0}".format(filetime))
        now = time.time()
        delta = dt.timedelta(seconds=now - filetime)
    
    return delta

def get_and_save_data_from_quandl():
    contract_df = pd.DataFrame()

    try:
        contract_df = get_leanhog_contract_data()
        with open(data_filename, 'wb') as fi:
            pickle.dump(contract_df, fi)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    
    return contract_df

def load_existing_data_file():
    contract_df = pd.DataFrame()

    try:
        histContractDataFile = Path(data_filename)
        if histContractDataFile.is_file():
            print('Loading data from \'{0}\''.format(data_filename))
            contract_df = pd.read_pickle(data_filename)
        else:
            print('histContractDataFile \'{0}\' is not a file'.format(data_filename))
            contract_df = get_and_save_data_from_quandl()
    except:
        print("Unexpected error:", sys.exc_info()[0])
    
    return contract_df

def get_leanhog_contract_data():
    print("Loading from Quandl webservice")
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