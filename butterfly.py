import sys
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day, not birthday...
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

import numpy as np
from numpy import nan
import datetime as dt

import lhdata as lhdata
import dataManager as dm

# Matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import seaborn as sns
from cycler import cycler
import itertools

import datetime as dt
import calendar
import pandas as pd
from pandas import TimeGrouper


import numpy as np
from numpy import nan
import math
import utility as utils
from exceptions import ContractException

def butterfly_calc(row):
    
    # Butterfly calc
    # Given 3 contracts: x,y,z
    # x+(-2y)+z

    x = row.iloc[0]
    y = row.iloc[1]
    z = row.iloc[2]

    if x == 0:
        return None
    if y == 0:
        return None
    if z == 0:
        return None
    
    # http://jonathansoma.com/lede/foundations/classes/pandas%20columns%20and%20functions/apply-a-function-to-every-row-in-a-pandas-dataframe/
    return row.iloc[0]+(-2*row.iloc[1])+row.iloc[2]

def butterfly(data, contractsTuple, contractExpiryYear):
    
    x = get_contract_data(data, contractsTuple[0], contractExpiryYear)  ## returns a Series (column)
    y = get_contract_data(data, contractsTuple[1], contractExpiryYear)
    z = get_contract_data(data, contractsTuple[2], contractExpiryYear)
    
    if(x.empty):
        raise ContractException("The {} contract in {} was not valid".format(contractsTuple[0], contractExpiryYear))
    if(y.empty):
        raise ContractException("The {} contract in {} was not valid".format(contractsTuple[1], contractExpiryYear))
    if(z.empty):
        raise ContractException("The {} contract in {} was not valid".format(contractsTuple[2], contractExpiryYear))

    bfdf = pd.concat([x,y,z], axis=1).dropna(thresh=3)
    bfSeries = bfdf.apply(butterfly_calc, axis=1).dropna() #.rolling(3).mean()
    
    bfdf['calc']= bfSeries
    
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(bfdf)

    return bfSeries

def create_chart(contractsTuple, selectedYears, selectedLayout, condensedQuartileOverrides):
    
    markers = itertools.cycle(('^', 'H', 'p', 'v', '*', 'H'))
    
    data = dm.load_data()
    seriesDf = pd.DataFrame()

    currYear = str(dt.date.today().year)
    # we're going to handle the present year as a special case, so remove it from the main list if it's present
    years = [yr for yr in selectedYears if str(yr) != currYear]
    
    # get first year
    firstYearSeries = butterfly(data, contractsTuple, years[0])
    graphStartDte = firstYearSeries.first_valid_index()
    graphEndDte = firstYearSeries.last_valid_index()
    
    # shift every other year to overlap their series
    for year in years:
        butterflySeries = butterfly(data, contractsTuple, year)
        daysToShift = (dt.datetime(int(year), graphStartDte.month, graphStartDte.day) - graphStartDte).days
        seriesDf[year] = butterflySeries.shift(-daysToShift, 'D')
    
    # shift the current year to overlap with the rest
    
    currYearButterfly = butterfly(data, contractsTuple, currYear)
    currYearShift = (dt.datetime(int(currYear), graphStartDte.month, graphStartDte.day) - graphStartDte).days
    seriesDf[currYear] = currYearButterfly.shift(-currYearShift, 'D')

    # calculate the mean and user selected percentiles for all years (minus the current contract)
    cols = [col for col in seriesDf if col not in [currYear]]
    seriesDf['historicalMean'] = seriesDf[cols].mean(axis=1)
    seriesDf['upperPercentile'] = seriesDf[cols].apply(lambda x: np.nanpercentile(x, condensedQuartileOverrides[0]), axis=1)
    seriesDf['lowerPercentile'] = seriesDf[cols].apply(lambda x: np.nanpercentile(x, condensedQuartileOverrides[1]), axis=1)
    
    plt.style.use('seaborn-colorblind')
    figure = plt.figure(num=1, figsize=(15,10), dpi=80)
    figure.suptitle("{0}-2*{1}+{2} BUTTERFLY".format(
        contractsTuple[0], 
        contractsTuple[1], 
        contractsTuple[2]))

    ax1 = figure.add_subplot(1,1,1)
    ax1.xaxis.set_major_locator(dates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%b'))
    
    ax1.grid(b=True, which='major', color='k', linewidth=0.5, linestyle='dashed')
    ax1.grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')
   
    # Historical mean (red)
    ax1.plot(seriesDf['historicalMean'],  color='red', linewidth=2.0, label='AVG', markevery=100, linestyle='dashed')

    # Current contract year + crosshair on todays date
    ax1.plot(seriesDf[currYear], label=currYear, linewidth=2, color='black', linestyle='solid')
    ax1.axvline(seriesDf[currYear].last_valid_index(), color='blue', linewidth=1.75)
    ax1.axhline(seriesDf[currYear][seriesDf[currYear].last_valid_index()], color='blue', linewidth=1.75)

    # Selected historical years
    if selectedLayout == 'Condensed':
        # Fill between 25-75 percentile
        # https://www.dasca.org/world-of-big-data/article/identifying-and-removing-outliers-using-python-packages
        ax1.fill_between(seriesDf.index, 
                seriesDf['upperPercentile'].rolling(window=1, min_periods=1).mean(), 
                seriesDf['lowerPercentile'].rolling(window=1, min_periods=1).mean(), 
                color='#FFF717',
                #color='#DEE2E3',
                alpha=0.4)
    else: 
        # Plot all the years except this year (already done above)
        for idx, year in enumerate(years):
            ax1.plot(seriesDf[year], label=get_legend_name(contractsTuple, year), lineWidth=1.1, marker=next(markers), markevery=10+(2*idx))

        if selectedLayout == 'Both':
            ax2 = figure.add_subplot(3,2,1)
            ax2.plot(seriesDf[currYear], label=currYear, linewidth=1.5, color='black', markevery=100)
            ax2.fill_between(seriesDf.index, 
                    seriesDf['upperPercentile'].rolling(window=1, min_periods=1).mean(), 
                    seriesDf['lowerPercentile'].rolling(window=1, min_periods=1).mean(), 
                    color='#FFF717',
                    #color='#DEE2E3',
                    alpha=0.4)
            ax2.yaxis.tick_right()
            ax2.xaxis.set_major_locator(dates.MonthLocator(interval=2))
            ax2.xaxis.set_major_formatter(dates.DateFormatter('%b'))
    

    legend = ax1.legend(loc='lower left', ncol=2, frameon=False)
    frame = legend.get_frame()
    frame.set_facecolor('white')

    plt.tight_layout()
    plt.show()


def get_legend_name(contractsTuple, contractExpiryYear):
    return "{0}".format(contractExpiryYear)

def get_contract_data(dataFrame, contractName, year):
    contractColumn = pd.DataFrame()
    colName = "{0}{1}".format(contractName, year)

    if colName in dataFrame.columns:
        contractColumn = dataFrame[colName]
        contractColumn.dropna(inplace=True)
        idx = pd.date_range(contractColumn.first_valid_index(), contractColumn.last_valid_index())
        contractColumn = contractColumn.reindex(idx, fill_value=np.nan)
        contractColumn.fillna(method='ffill', limit=3, inplace=True)
    
    return contractColumn

def get_contract_expiry_date(contractName, expiryYear):
    # Last trading day is the 10th business day of the month @ 12pm
    # http://www.wikinvest.com/futures/Lean_Hogs_Futures
    contractMonth = utils.months[contractName]
    firstOfMonth = dt.datetime(expiryYear, contractMonth, 1, 0, 0)
    
    return firstOfMonth + BDay(10)


def get_contract_start_date(contractName, expiryYear):
    contractEndDate = get_contract_expiry_date(contractName, year)
    startDate = contractEndDate - relativedelta(years=1) 

    return startDate
