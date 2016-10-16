import datetime as dt
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day, not birthday...
import Quandl as q

import numpy as np
from numpy import nan

def get_online_lh_data(years, months):
    recordList = []
    columnList = []
    columnRenameDict = {}
    for year in years :
        for k,v in months.items() :
            s = "CME/LN{0}{1}".format(v,year)
            recordList.append(s)
            t = "CME.LN{0}{1} - Settle".format(v,year)
            tx = "LN{0}{1}".format(v,year)
            columnList.append(t)
            columnRenameDict.update({t:tx})

    df = q.get(
        recordList, 
        authtoken= "dXzByDoZicZy-WFvPyTf")[
            columnList]

    df.rename(columns=columnRenameDict, inplace=True)
    
    return df

def get_expiry_date_for_month(month, year):
    firstOfMonth = dt.datetime(year, month, 1, 0, 0)
    # Last trading day is the 10th business day of the month @ 12pm
    # http://www.wikinvest.com/futures/Lean_Hogs_Futures
    # but these numbers don't match the days at
    # http://www.barchart.com/futures/expirations.php
    expiry = firstOfMonth + BDay(10)

    return expiry

def get_contract(data, contractName):
    single = data[contractName]
    single.dropna(inplace=True)
    idx = pd.date_range(single.first_valid_index(), single.last_valid_index())
    single = single.reindex(idx, fill_value=np.nan)
    single.fillna(method='ffill', limit=3, inplace=True)
    
    return single

def print_df(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')



def plot_multiple_avgs(srcDf, pltMap, currYearColName):
    # Matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import matplotlib.dates as dates
    import seaborn as sns
    
    # create a new dataframe with the same date range as the existing
    # We'll then put all the different means we want into this one
    avgsDf = pd.DataFrame(index=srcDf.index)

    for key,val in pltMap.items() :
        avgsDf[key] = srcDf[val].mean(axis=1)


    fig, ax = plt.subplots(figsize=(15, 8), dpi=70)
    ax.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(dates.YearLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n %Y'))
    for i, c in enumerate(avgsDf.columns):
        ax.plot(avgsDf[c], label=c, linewidth=1)

    #plot current year
    col = srcDf[currYearColName]
    ax.plot(col, label=c, linewidth=3, color='black')
    ax.axvline(col.last_valid_index())
    ax.axhline(col[col.last_valid_index()])
    ax.annotate(dt.date.today().strftime("%B %d"),
            (col.last_valid_index(), col[col.last_valid_index()]),
            xytext=(35, 35), 
            textcoords='offset points',
            arrowprops=dict(arrowstyle='-|>'),
            fontsize=22)
    avgsDf['Current'] = col


    plt.grid()
    plt.legend()
    plt.show()

    return avgsDf