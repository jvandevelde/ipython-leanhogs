import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day, not birthday...
from dateutil.relativedelta import relativedelta


import numpy as np
from numpy import nan
import datetime as dt

import lhdata

origMonths = { 
    2:'G', # Feb
    4:'J', # Apr
    5:'K', #May    
    6:'M', #Jun 
    7:'N', #Jul
    8:'Q', #Aug
    10:'V', #Oct
    12:'Z' #Dec 
}

months = { 
    'G':2, # Feb
    'J':4, # Apr
    'K':5, #May    
    'M':6, #Jun 
    'N':7, #Jul
    'Q':8, #Aug
    'V':10, #Oct
    'Z':12  #Dec 
}

regularMonthSets = {
    'G':['J','K','M'],
    'J':['K','M','N'],
    'K':['M','N','Q'],
    'M':['N','Q','V'],
    'N':['Q','V','Z'],
    'Q':['V','Z','G'],
    'V':['Z','G','J'],
    'Z':['G','J','K']
}

allYears = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

#df = lhdata.get_online_lh_data(allYears, months)
#df.to_pickle('data.pickle')

def get_active_years():
    activeYears = []
    thisYear = dt.date.today().year
    activeYears.append(thisYear)
    activeYears.append(thisYear + 1)
    print(activeYears)
    return activeYears


def get_contract_expiry_date(contractName, expiryYear):
    # Last trading day is the 10th business day of the month @ 12pm
    # http://www.wikinvest.com/futures/Lean_Hogs_Futures
    contractMonth = months[contractName]
    firstOfMonth = dt.datetime(expiryYear, contractMonth, 1, 0, 0)
    
    return firstOfMonth + BDay(10)


def get_contract_start_date(contractName, year):
    contractEndDate = get_contract_expiry_date(contractName, year)
    startDate = contractEndDate - relativedelta(years=1) 

    return startDate


def get_contract_data(data, contractName, year):
    colName = "{0}{1}".format(contractName, year)
    single = data[colName]
    single.dropna(inplace=True)
    idx = pd.date_range(single.first_valid_index(), single.last_valid_index())
    single = single.reindex(idx, fill_value=np.nan)
    single.fillna(method='ffill', limit=3, inplace=True)
    
    return single

def calculate(near, historicalYears):
    historicalYears.extend(get_active_years())
    years = historicalYears

    nearContractMonthLetter = near[2]
    print('Start Date: {0}\nEnd Date:{1}'.format(
        get_contract_start_date(nearContractMonthLetter, dt.date.today().year),
        get_contract_expiry_date(nearContractMonthLetter, dt.date.today().year)))
    
    far = ["LN{0}".format(item) for item in regularMonthSets[nearContractMonthLetter]]
    print(far)
    
    df = pd.read_pickle('data.pickle')
    xlsWriter = pd.ExcelWriter('output/workingData.xlsx', 
                            engine='xlsxwriter',
                            datetime_format='mmm dd, yyyy',
                            date_format='mmm dd, yyyy')

    df.to_excel(xlsWriter, sheet_name='Original')



    for year in years:
        cols = []
        worksheetName = 'LNK {0}'.format(year)
        cols.append('{0}{1}'.format(near, year))
        #print("Calculating working datasets for {0}".format(year))
        for fcn in far:
            cols.append('{0}{1}'.format(fcn, year))
        
        # DropNA http://stackoverflow.com/questions/13413590/how-to-drop-rows-of-pandas-dataframe-whose-value-of-certain-column-is-nan
        dfSubset = pd.DataFrame(df[cols])
        dfSubset.dropna(inplace=True, how='all')
        # Improving Pandas Excel output
        # http://pbpython.com/improve-pandas-excel-output.html
        # dfSubset = dfSubset.assign(diff1=(dfSubset[dfSubset.columns[0]] - dfSubset[dfSubset.columns[1]]))
        for fcn in far:
            colName = 'diff_{0}_{1}'.format(near,fcn)
            dfSubset[colName] = dfSubset['{0}{1}'.format(near, year)] - dfSubset['{0}{1}'.format(fcn, year)]
            
        dfSubset.to_excel(xlsWriter, sheet_name=worksheetName)
        worksheet = xlsWriter.sheets[worksheetName]
        worksheet.set_column('A:A', 18)

    finalDataXlsWriter = pd.ExcelWriter('output/finalData.xlsx', 
                            engine='xlsxwriter',
                            datetime_format='mmm dd',
                            date_format='mmm dd')
    
    
    graphStartDte = get_contract_start_date(nearContractMonthLetter, dt.date.today().year)
    graphEndDte = get_contract_expiry_date(nearContractMonthLetter, dt.date.today().year)
    print("Graph strt/end: {0} - {1}".format(graphStartDte, graphEndDte))
    
    dfList = []  
    for farContractName in far :
        
        idx = pd.date_range(graphStartDte, graphEndDte)
        dfDiffsShifted = pd.DataFrame(index=idx)
        
        idxOriginal = pd.date_range(df.first_valid_index(), df.last_valid_index())
        dfDiffsOriginalDtes = pd.DataFrame(index=idxOriginal)


        for year in years :
            print('Working on year {0}'.format(year))
            colName = lhdata.get_diff_col_name(year)
            
            nearContractData = get_contract_data(df, near, year)
            farContractData = get_contract_data(df, farContractName, year)

            difference = nearContractData.subtract(other=farContractData, fill_value=np.nan)
            difference.dropna(inplace=True)
            
            dfDiff = pd.DataFrame(difference, columns=[colName])
            

            diffStartDte = get_contract_start_date(nearContractMonthLetter, year)
            diffEndDte = get_contract_expiry_date(nearContractMonthLetter, year)

            #print("Diff strt/end: {0} - {1}".format(diffStartDte, diffEndDte))
            idx = pd.date_range(diffStartDte, diffEndDte)
            dfDiff = dfDiff.reindex(idx, fill_value=np.nan)

            #### Need to figure out the number of days between 
            daysToShift = (dfDiff.first_valid_index() - graphStartDte).days
            ## Concat http://chrisalbon.com/python/pandas_join_merge_dataframe.html
            dfDiffsOriginalDtes = pd.concat([dfDiffsOriginalDtes, dfDiff], axis=1)
            shifted = dfDiff.shift(-daysToShift, 'D')
            dfDiffsShifted = pd.concat([dfDiffsShifted, shifted], axis=1)

        dfDiffsShifted.dropna(thresh=1, inplace=True)
        dfDiffsOriginalDtes.dropna(thresh=1, inplace=True)
        
        dfList.append([farContractName, dfDiffsShifted, dfDiffsOriginalDtes])
        dfDiffsShifted.to_excel(finalDataXlsWriter, sheet_name=farContractName)

    finalDataXlsWriter.save()
    finalDataXlsWriter.close()
    xlsWriter.save()
    xlsWriter.close()

    return dfList