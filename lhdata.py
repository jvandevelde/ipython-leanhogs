# Matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import seaborn as sns

import datetime as dt
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day, not birthday...
import Quandl as q

import numpy as np
from numpy import nan
import math

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
    # create a new dataframe with the same date range as the existing
    # We'll then put all the different means we want into this one
    avgsDf = pd.DataFrame(index=srcDf.index)

    for key,val in pltMap.items() :
        colNames = [get_diff_col_name(item) for item in val]
        print(colNames)
        avgsDf[key] = srcDf[colNames].mean(axis=1)


    fig, ax = plt.subplots(figsize=(15, 8), dpi=70)
    ax.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(dates.YearLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter(''))
    for i, c in enumerate(avgsDf.columns):
        ax.plot(avgsDf[c], label=c, linewidth=1)

    #plot current year
    col = srcDf[get_diff_col_name(currYearColName)]
    ax.plot(col, label="Current", linewidth=3, color='black')
    ax.axvline(col.last_valid_index())
    ax.axhline(col[col.last_valid_index()])
    ax.annotate(dt.date.today().strftime("%B %d"),
            (col.last_valid_index(), col[col.last_valid_index()]),
            xytext=(35, 35), 
            textcoords='offset points',
            arrowprops=dict(arrowstyle='-|>'),
            fontsize=18)
    avgsDf['Current'] = col


    plt.grid()
    plt.legend()
    plt.show()

    return avgsDf

def get_diff_col_name(year) :
    return 'diff_{0}'.format(year)
    
def plot_df(df, currYearColName, title):
    #http://stackoverflow.com/questions/14888473/python-pandas-dataframe-subplot-in-columns-and-rows
    #http://stackoverflow.com/questions/14770735/changing-figure-size-with-subplots
    f2, axes = plt.subplots(ncols=2, nrows=math.ceil(df.columns.size/2), figsize=(20,10), dpi=80)
    
    #f2.set_size_inches(20,10) # width, height
    #f2.set_dpi(80)
    
    for i, c in enumerate(df.columns):
        if(i==0):
            df[c].plot(ax=axes[0,0])
            df[currYearColName].plot(ax=axes[0,0], color='black', lw=1.2)
            axes[0,0].set_title('{0} {1}'.format(title,c))
            axes[0,0].xaxis.set_minor_locator(dates.MonthLocator(interval=4))
            axes[0,0].xaxis.set_minor_formatter(dates.DateFormatter('%b'))
            axes[0,0].xaxis.set_major_locator(dates.YearLocator())
            axes[0,0].xaxis.set_major_formatter(dates.DateFormatter(''))
            axes[0,0].grid(b=True, which='major', color='w', linewidth=1.0)
            axes[0,0].grid(b=True, which='minor', color='w', linewidth=0.5)
            legend = axes[0,0].legend(frameon=True, loc='center left', bbox_to_anchor=(1,0.5),
                                fancybox=True, shadow=True)
            frame = legend.get_frame()
            frame.set_facecolor('white')
        else:
            axis = axes[math.floor(i/2),i%2]
            df[c].plot(ax=axis)
            df[currYearColName].plot(ax=axis, color='black', lw=1.2)
            axis.set_title('{0} {1}'.format(title,c))
            axis.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
            axis.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
            axis.xaxis.set_major_locator(dates.YearLocator())
            axis.xaxis.set_major_formatter(dates.DateFormatter(''))
            axis.grid(b=True, which='major', color='w', linewidth=1.0)
            axis.grid(b=True, which='minor', color='w', linewidth=0.5)
            legend = axis.legend(frameon=True, loc='center left', bbox_to_anchor=(1,0.5),
                                fancybox=True, shadow=True)
            frame = legend.get_frame()
            frame.set_facecolor('white')
    
    f2.set_tight_layout(True)
    