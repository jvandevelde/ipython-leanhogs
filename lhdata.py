# Matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import seaborn as sns

import datetime as dt
import pandas as pd
from pandas import TimeGrouper

import numpy as np
from numpy import nan
import math
import utility as utils

def calculate_custom_historical_series(srcDf, pltMap):
    # create a new dataframe with the same date range as the existing
    # We'll then put all the different means we want into this one
    avgsDf = pd.DataFrame(index=srcDf.index)

    for key,val in pltMap.items() :
        colNames = [str(item) for item in val]
        avgsDf[key] = srcDf[colNames].mean(axis=1)
    
    currYearColName = get_most_recent_year_column_name(srcDf)
    col = srcDf[currYearColName]

    avgsDf['Current'] = col

    return avgsDf

def plot_custom_historical_series(srcDf, pltMap, title):
    currYearColName = get_most_recent_year_column_name(srcDf)
    avgsDf = calculate_custom_historical_series(srcDf, pltMap)

    fig, ax = plt.subplots(figsize=(15, 8), dpi=70)
    
    ax.xaxis.set_major_locator(dates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%b-01'))
    ax.xaxis.set_minor_locator(dates.DayLocator(bymonthday=[14, 21], interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
    
    ax.grid(b=True, which='major', color='w', linewidth=1.5)
    ax.grid(b=True, which='minor', color='w', linewidth=1.0)

    # plot everything but the current year
    cols = [col for col in avgsDf.columns if col not in ['Current']]
    for i, c in enumerate(cols):
        ax.plot(avgsDf[c], label=c, linewidth=1)

    #plot current year
    col = srcDf[currYearColName]
    ax.plot(col, label="Current", linewidth=3, color='black')
    ax.axvline(col.last_valid_index())
    ax.axhline(col[col.last_valid_index()])
    ax.annotate(dt.date.today().strftime("%b %d"),
            (col.last_valid_index(), col[col.last_valid_index()]),
            xytext=(-45, 60), 
            textcoords='offset points',
            arrowprops=dict(arrowstyle='-|>'),
            fontsize=16)
    
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')

    plt.title(title)
    plt.legend()
    plt.show()

def get_most_recent_year_column_name(df):
    currYear = dt.datetime.now().year
    currYearColName = str(currYear)
    if(str(currYear + 1) in df.columns):
        currYearColName = str(currYear + 1)

    return currYearColName

def plot_individual_against_current(dfList, near):
    
    
    for pair in dfList:
        df = pair[1]

        dfCleaned = pd.DataFrame(df)
        df = dfCleaned.dropna(thresh=1)
        currYearColName = get_most_recent_year_column_name(df)

        #http://stackoverflow.com/questions/14888473/python-pandas-dataframe-subplot-in-columns-and-rows
        #http://stackoverflow.com/questions/14770735/changing-figure-size-with-subplots
        f2, axes = plt.subplots(ncols=2, nrows=math.ceil(df.columns.size/2), figsize=(20,10), dpi=80)
        
        #f2.set_size_inches(20,10) # width, height
        #f2.set_dpi(80)

        title = 'Individuals {0}-{1}'.format(near, pair[0])

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
        f2.suptitle = title
    
    plt.show()

def get_month_label(x, pos=None):
    x = dates.num2date(x)
    return x.strftime('%b-01')[0]

def plot_seasonal_boxplot(dataList, nearContract):
    #pd.options.display.mpl_style = 'default'
    i = 1
    x = sorted(list(utils.allMonths.values()))
    month = utils.months[nearContract[2]]
    rotatedMonths = x[month: ] + x[ :month]
    print(rotatedMonths)
    idx = rotatedMonths.index(month)
    print("index {0}".format(rotatedMonths.index(month)))
    print([(x - (idx-1)) + len(rotatedMonths) for x in rotatedMonths])
    for listItems in dataList:
        df = listItems[2]
        cols = list(df.columns.values)
        
        df['sum'] = df[cols].sum(axis=1)
        df['count'] = df[cols].count(axis=1)
        df['month'] = df.index.month
        
        
        
        #http://machinelearningmastery.com/time-series-data-visualization-with-python/
        #fig = plt.figure(1, figsize=(9, 6))
        # Create an axes instance
        #ax = fig.add_subplot(3,1,i)
        #i=i+1

        # Create the boxplot
        #bp = ax.boxplot(df['sum'],showfliers=True, sym='k.')
        #plt.ylim(ymin=-60, ymax=60)
        #bp = sns.boxplot(df['sum'],ax=ax)
        
        #print(df)
        print(x[month:])
        ax = df.boxplot(column=['sum'], by='month', showmeans=True, positions=rotatedMonths)
        # set your own proper title
        plt.title("{0}-{1}".format(nearContract, listItems[0]))
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")
        plt.show()

        #df['sum'].hist()


def plot_continual_spread_set(dataList, nearContract):
    figure = plt.figure(num=1, figsize=(15,10), dpi=80)
    j = 1

    for listItems in dataList:
        print("Plotting {0}-{1}".format(nearContract, listItems[0]))
        farContractName = listItems[0]
        df = listItems[2]
        

        ax1 = figure.add_subplot(3,1,j)
        #ax.set_prop_cycle(cycler('color', ['c', 'm', 'y', 'k']) +
        #                   cycler('lw', [1, 2, 3, 4]))
        ax1.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
        ax1.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
        ax1.xaxis.set_major_locator(dates.YearLocator())
        ax1.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
        
        # origCols = [col for col in df.columns if col.startswith('orig_')]

        for col in df.columns:
            # if we're looking at this year (current) contract, let's plot a thick/black line
            # with a vertical/horizontal crosshair to make it easy to look at
            if(col == '{0}'.format(get_most_recent_year_column_name(df))) :
                ax1.plot(df[col].rolling(window=7, min_periods=7).mean(), label=col, color='black', lineWidth=2)
            # normal case is to display a thin line for historical years
            else :
                ax1.plot(df[col].rolling(window=7, min_periods=7).mean(), label='{0}'.format(col), lineWidth=0.5, linestyle='-')
                
        ax1.grid(b=True, which='major', color='w', linewidth=1.5)
        ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
        # Shrink current axis by 20%
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.88, box.height])

        # Put a legend to the top of the current axis
        legend = ax1.legend(frameon=True, loc='center left', bbox_to_anchor=(1,0.5),
                            fancybox=True, shadow=True)
        frame = legend.get_frame()
        frame.set_facecolor('white')
        ax1.set_title('Continuous {0} - {1}'.format(nearContract, farContractName))


        j+=1

    #plt.suptitle('{0} Data'.format(nearContract))
    plt.tight_layout()
    plt.show()

def plot_historical_comparison(tupleList, near):
    f1 = plt.figure(num=1, figsize=(15, 10), dpi=80)
    
    j = 1
    
    for pair in tupleList:
        print("Plotting {0}-{1}".format(near, pair[0]))
        farContractName = pair[0]

        ###########
        # plot shifted data with the mean
        ###########
        df = pair[1]

        shiftedCols = [col for col in df.columns]
        
        ax2 = f1.add_subplot(3,1,j)
        ax2.xaxis.set_major_locator(dates.MonthLocator(interval=1))
        #ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos: get_month_label(x)))
        ax2.xaxis.set_major_formatter(dates.DateFormatter('%b-01'))
        
        ax2.xaxis.set_minor_locator(dates.DayLocator(bymonthday=[14, 21], interval=1))
        ax2.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
        
        #ax2.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=dates.FRIDAY))
        #ax2.xaxis.set_minor_formatter(dates.DateFormatter('|'))
        
        currYearColName = get_most_recent_year_column_name(df)
        for i, c in enumerate(shiftedCols):
            l = None
            if(c == currYearColName):
                ax2.plot(df[c], label=c, linewidth=2, color='black')
                ax2.axvline(df[c].last_valid_index())
                ax2.axhline(df[c][df[c].last_valid_index()])
                ax2.annotate(dt.date.today().strftime("%b %d"),
                     (df[c].last_valid_index(), df[c][df[c].last_valid_index()]),
                     xytext=(40, -40), 
                     textcoords='offset points',
                     arrowprops=dict(arrowstyle='-|>'),
                     fontsize=16)
            else:
                ax2.plot(df[c], label=c, linewidth=1)
            
        # calculate the mean for all years (minus the current contract) and plot it
        cols = [col for col in shiftedCols if col not in [currYearColName]]
        df['mean'] = df[cols].mean(axis=1)
        
        ax2.plot(df['mean'], color='red', linewidth=1.5, label='AVG')
        shiftedCols = [col for col in df.columns if col.startswith('orig_') == False]

        # Shrink the x-axis and place the legend on the outside
        # http://stackoverflow.com/a/4701285
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0, box.width * 0.92, box.height * 0.90])
        legend = ax2.legend(frameon=True, loc='center left', bbox_to_anchor=(1,0.5),
                            fancybox=True, shadow=True, ncol=2)
        frame = legend.get_frame()
        frame.set_facecolor('white')

        ax2.set_title('Overlay {0} - {1}'.format(near, farContractName))
        ax2.grid(b=True, which='major', color='w', linewidth=1.5)
        ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
        
        # rotate major tick labels to avoid overlapping
        # http://stackoverflow.com/a/28063506
        plt.setp(ax2.get_xticklabels(), rotation=30, horizontalalignment='right')
        #plt.subplots_adjust(hspace=0.3)    # this does not seem to work with ax.set_position() above - it causes that call to not be executed

        j+=1
    
    plt.suptitle('Historic Data for {0}'.format(near))
    plt.show()
