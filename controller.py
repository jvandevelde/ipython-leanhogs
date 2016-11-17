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


def get_expiry_date_for_month(nearContract):
    # Last trading day is the 10th business day of the month @ 12pm
    # http://www.wikinvest.com/futures/Lean_Hogs_Futures

    currentDate = dt.date.today()
    expiryYear = currentDate.year + 1
    contractMonth = months[nearContract]

    if currentDate.month <= contractMonth:
        expiryYear =  currentDate.year

    firstOfMonth = dt.datetime(expiryYear, contractMonth, 1, 0, 0)
    
    return firstOfMonth + BDay(10)


def get_graph_start_date(nearContract):
    contractEndDate = get_expiry_date_for_month(nearContract)
    startDate = contractEndDate - relativedelta(years=1) 

    return startDate


def calculate(near, historicalYears):
    historicalYears.extend(get_active_years())
    years = historicalYears

    contractLetter = near[2]
    print('Start Date: {0}\nEnd Date:{1}'.format(
        get_graph_start_date(contractLetter),
        get_expiry_date_for_month(contractLetter)))
    
    far = ["LN{0}".format(item) for item in regularMonthSets[contractLetter]]
    print(far)
    
    df = pd.read_pickle('data.pickle')
    xlsWriter = pd.ExcelWriter('output/workingData.xlsx', 
                            engine='xlsxwriter',
                            datetime_format='mmm dd, yyyy',
                            date_format='mmm dd, yyyy')

    df.to_excel(xlsWriter, sheet_name='Original')

    dfList = []  

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
    
    
    for farContractName in far :
        dfDiffs = pd.DataFrame()
        #print("Calculating shifted datasets {0}-{1}".format(near, farContractName))

        for year in years :
            colName = lhdata.get_diff_col_name(year)
            
            nearContractData = lhdata.get_contract(df, "{0}{1}".format(near, year))
            farContractData = lhdata.get_contract(df, "{0}{1}".format(farContractName, year))
            difference = nearContractData.subtract(other=farContractData, fill_value=np.nan)
            difference.dropna(inplace=True)
            
            dfDiff = pd.DataFrame(difference, columns=[colName])


            currMinIndex = dfDiffs.first_valid_index()
            if (currMinIndex is None or dfDiff.first_valid_index() < currMinIndex) :
                fvi = dfDiff.first_valid_index()
            else :
                fvi = dfDiffs.first_valid_index()
                
            lvi = dfDiff.last_valid_index()

            idx = pd.date_range(fvi,lvi)
            dfDiffs = dfDiffs.reindex(idx, fill_value=np.nan)

            #### Need to figure out the number of days between 
            #dfDiff[colName][dfDiff.first_valid_index()] = -9999
            daysToShift = (dfDiff.first_valid_index() - fvi).days
            dfDiffs[['orig_{0}'.format(colName)]] = dfDiff[[colName]]
            dfDiffs[[colName]] = dfDiff[[colName]].shift(-daysToShift, 'D')

        dfDiffs.dropna(thresh=1, inplace=True)

        dfList.append([farContractName,dfDiffs])
        shiftedDiffColumnNames = [col for col in dfDiffs.columns if col.startswith('diff_')]
        dfDiffs[shiftedDiffColumnNames].to_excel(finalDataXlsWriter, sheet_name=farContractName)

    finalDataXlsWriter.save()
    finalDataXlsWriter.close()
    xlsWriter.save()
    xlsWriter.close()

    return dfList