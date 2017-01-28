# Matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import seaborn as sns
from cycler import cycler

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
    ax.xaxis.set_minor_locator(dates.DayLocator(bymonthday=[15], interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
    
    ax.grid(b=True, which='major', color='k', linewidth=1.0, linestyle='dashed')
    ax.grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')

    # plot everything but the current year
    cols = [col for col in avgsDf.columns if col not in ['Current']]
    for i, c in enumerate(cols):
        ax.plot(avgsDf[c], label=c, linewidth=1)

    #plot current year
    col = srcDf[currYearColName]
    ax.plot(col, label="Curr.", linewidth=1.75, color='black')
    
    ax.axvline(col.last_valid_index(), color='blue', linewidth=1.75)
    ax.axhline(col[col.last_valid_index()], color='blue', linewidth=1.75)

    # print arrow annotation to current date
    #ax.annotate(dt.date.today().strftime("%b %d"),
    #        (col.last_valid_index(), col[col.last_valid_index()]),
    #        xytext=(-45, 60), 
    #        textcoords='offset points',
    #        arrowprops=dict(arrowstyle='-|>'),
    #        fontsize=16)
    
    legend = ax.legend(loc='lower left', frameon=True, shadow=True)

    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.title(title)
    
    plt.show()

def get_most_recent_year_column_name(df):
    currYear = dt.datetime.now().year
    currYearColName = str(currYear)
    if(str(currYear + 1) in df.columns):
        currYearColName = str(currYear + 1)

    return currYearColName

def plot_individual_against_current(dfList, near, selected_far_contracts):
    for pair in dfList:
        farContractName = pair[0]
        if(farContractName[2] not in selected_far_contracts):
            continue
        
        df = pair[1]
        dfCleaned = pd.DataFrame(df)
        df = dfCleaned.dropna(thresh=1)
        currYearColName = get_most_recent_year_column_name(df)

        #http://stackoverflow.com/questions/14888473/python-pandas-dataframe-subplot-in-columns-and-rows
        #http://stackoverflow.com/questions/14770735/changing-figure-size-with-subplots
        f2, axes = plt.subplots(ncols=2, nrows=math.ceil(df.columns.size/2), figsize=(20,10), dpi=80)
        title = '{0} - {1}'.format(near, farContractName)

        for i, c in enumerate(df.columns):
            if(i==0):
                df[c].plot(ax=axes[0,0], color='magenta', lw=1.0)
                df[currYearColName].plot(ax=axes[0,0], color='black', lw=1.8)
                axes[0,0].set_title('{0} {1}'.format(title,c))
                axes[0,0].xaxis.set_minor_locator(dates.MonthLocator(interval=2))
                axes[0,0].xaxis.set_minor_formatter(dates.DateFormatter('%b'))
                axes[0,0].xaxis.set_major_locator(dates.YearLocator())
                axes[0,0].xaxis.set_major_formatter(dates.DateFormatter(''))
                axes[0,0].grid(b=True, which='major', color='k', linewidth=0.5, linestyle='dotted')
                axes[0,0].grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')
            else:
                axis = axes[math.floor(i/2),i%2]
                df[c].plot(ax=axis, color='magenta', lw=1.0)
                df[currYearColName].plot(ax=axis, color='black', lw=1.8)
                axis.set_title('{0} {1}'.format(title,c))
                axis.xaxis.set_minor_locator(dates.MonthLocator(interval=2))
                axis.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
                axis.xaxis.set_major_locator(dates.YearLocator())
                axis.xaxis.set_major_formatter(dates.DateFormatter(''))
                axis.grid(b=True, which='major', color='k', linewidth=0.5, linestyle='dotted')
                axis.grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')
        
        f2.set_tight_layout(True)
        f2.suptitle = title
    
    plt.show()

def get_month_label(x, pos=None):
    x = dates.num2date(x)
    return x.strftime('%b-01')[0]

def plot_monthly_seasonal_boxplot(dataList, nearContract, selected_far_contracts):
    #pd.options.display.mpl_style = 'default'
    
    x = sorted(list(utils.allMonths.values()))
    month = utils.months[nearContract[2]]
    rotatedMonths = x[month: ] + x[ :month]
    #print(rotatedMonths)
    idx = rotatedMonths.index(month)
    #print("index {0}".format(rotatedMonths.index(month)))
    #print([(x - (idx-1)) + len(rotatedMonths) for x in rotatedMonths])

    i = 1
    for listItems in dataList:
        farContractName = listItems[0]
        if(farContractName[2] not in selected_far_contracts):
            continue
        
        dfUnshifted = listItems[2]
        cols = list(dfUnshifted.columns.values)
        
        dfUnshifted['value'] = dfUnshifted[cols].sum(axis=1)
        dfUnshifted['count'] = dfUnshifted[cols].count(axis=1)
        dfUnshifted['month'] = dfUnshifted.index.month
        month = dt.date.today().month

        #http://machinelearningmastery.com/time-series-data-visualization-with-python/

        fig = plt.figure(i, figsize=(12,9))

        subplot = fig.add_subplot(2,1,1)
        ax = sns.boxplot(x='month', y='value', data=dfUnshifted, showfliers=False, color=None, hue=None)
        #ax = sns.swarmplot(x="month", y="value", data=dfUnshifted, color=".25")
        
        for j in range(1,13):
            y = dfUnshifted.value[dfUnshifted.month == j].dropna()
            # Add some random "jitter" to the x-axis
            x = np.random.normal(j, 0.04, size=len(y))
            ax.plot(x-1, y, 'r.', alpha=0.2)

        ax.axvspan(month - 0.5, month + 0.5, alpha=0.75, color='#DEE2E3')

        # set your own proper title
        plt.title("{0}-{1}".format(nearContract, listItems[0]))
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")

        ax.grid(b=False, which='major', color='k', linewidth=0.5, linestyle='dotted')
        ax.grid(b=False, which='minor', color='k', linewidth=0.5, linestyle='dotted')
        
        for j in range(0,12):
            mybox = ax.artists[j]
            # Change the appearance of that box
            mybox.set_facecolor('white')    

        mybox = ax.artists[month]

        # Change the appearance of that box
        mybox.set_facecolor('white')
        mybox.set_edgecolor('black')
        mybox.set_alpha(0.75)
        mybox.set_linewidth(2)

        sp2 = fig.add_subplot(2,1,2)
        dfShifted = listItems[1]
        
        currYearColName = get_most_recent_year_column_name(dfShifted)
        
        sp2.plot(dfShifted[currYearColName], label='Curr', linewidth=1.5, color='black', markevery=100)
        sp2.axvline(dfShifted[currYearColName].last_valid_index(), color='blue', linewidth=1.75)
        sp2.axhline(dfShifted[currYearColName][dfShifted[currYearColName].last_valid_index()], color='blue', linewidth=1.75)
        
        # calculate the mean for all years (minus the current contract) and plot it
        shiftedCols = [col for col in dfShifted.columns]
        cols = [col for col in shiftedCols if col not in [currYearColName]]
        dfShifted['mean'] = dfShifted[cols].mean(axis=1)
    
        sp2.plot(dfShifted['mean'], color='red', linestyle='dashed')
        
        # Highlighting
        period = dfShifted[(dfShifted.index.month >= month) & (dfShifted.index.month < month+1)].index
        sp2.axvspan(min(period), max(period), alpha=0.75, color='#DEE2E3')

        i = i+1
        fig.set_tight_layout(True)
    
    plt.show()

def plot_weekly_seasonal_boxplot(dataList, nearContract, selected_far_contracts):
    #pd.options.display.mpl_style = 'default'
    
    i = 1
    for listItems in dataList:
        farContractName = listItems[0]
        if(farContractName[2] not in selected_far_contracts):
            continue

        dfUnshifted = listItems[2]
        cols = list(dfUnshifted.columns.values)
        
        dfUnshifted['value'] = dfUnshifted[cols].sum(axis=1)
        dfUnshifted['count'] = dfUnshifted[cols].count(axis=1)
        dfUnshifted['wk'] = dfUnshifted.index.weekofyear

        #https://docs.python.org/3/library/datetime.html#datetime.date.isocalendar
        # Returns 3 tuple with ISO year, wk, wkday
        isoDate = dt.date.today().isocalendar()
        week = isoDate[1]

        #http://machinelearningmastery.com/time-series-data-visualization-with-python/

        fig = plt.figure(i, figsize=(12,9))

        subplot = fig.add_subplot(2,1,1)
        ax = sns.boxplot(x='wk', y='value', data=dfUnshifted, showfliers=False, color=None, hue=None)
        #ax = sns.swarmplot(x="month", y="value", data=dfUnshifted, color=".25")
        
        for j in range(1,54):
            
            y = dfUnshifted.value[dfUnshifted.wk == j].dropna()
            # Add some random "jitter" to the x-axis
            x = np.random.normal(j, 0.04, size=len(y))
            ax.plot(x-1, y, 'r.', alpha=0.2)

        # subtract 1 to line up with x-axis that starts at 0, not 1
        ax.axvspan((week -1) - 0.5, (week - 1) + 0.5, alpha=0.75, color='#DEE2E3')

        plt.title("{0}-{1}".format(nearContract, listItems[0]))
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")

        ax.grid(b=False, which='major', color='k', linewidth=0.5, linestyle='dotted')
        ax.grid(b=False, which='minor', color='k', linewidth=0.5, linestyle='dotted')
        
        for j in range(0,53):
            mybox = ax.artists[j]

            # Change the appearance of that box
            mybox.set_facecolor('white')    

        mybox = ax.artists[week-1]

        # Change the appearance of that box
        mybox.set_facecolor('white')
        mybox.set_edgecolor('black')
        mybox.set_alpha(0.75)
        mybox.set_linewidth(2)

        sp2 = fig.add_subplot(2,1,2)
        dfShifted = listItems[1]
        
        currYearColName = get_most_recent_year_column_name(dfShifted)
        
        sp2.plot(dfShifted[currYearColName], label='Curr', linewidth=1.5, color='black', markevery=100)
        sp2.axvline(dfShifted[currYearColName].last_valid_index(), color='blue', linewidth=1.75)
        sp2.axhline(dfShifted[currYearColName][dfShifted[currYearColName].last_valid_index()], color='blue', linewidth=1.75)
 
        # calculate the mean for all years (minus the current contract) and plot it
        shiftedCols = [col for col in dfShifted.columns]
        cols = [col for col in shiftedCols if col not in [currYearColName]]
        dfShifted['mean'] = dfShifted[cols].mean(axis=1)

        sp2.plot(dfShifted['mean'], color='red', linestyle='dashed')
        
        # Highlighting
        period = utils.iso_to_gregorian(isoDate[0], isoDate[1], isoDate[2])
        range_start = utils.add_years(dt.date.today() - dt.timedelta(days=isoDate[2]), -1)
        range_end = range_start + dt.timedelta(days=7)
        sp2.axvspan(range_start, range_end, alpha=0.75, color='#DEE2E3')
        
        i = i+1
    
        fig.set_tight_layout(True)
    
    plt.show()

def plot_continual_spread_set(dataList, nearContract, selected_far_contracts):
    figure = plt.figure(num=1, figsize=(15,10), dpi=80)
    j = 1

    for listItems in dataList:
       #print("Plotting {0}-{1}".format(nearContract, listItems[0]))
        farContractName = listItems[0]
        df = listItems[2]
        
        if(farContractName[2] not in selected_far_contracts):
            continue

        ax1 = figure.add_subplot(len(selected_far_contracts),1,j)
        #ax.set_prop_cycle(cycler('color', ['c', 'm', 'y', 'k']) +
        #                   cycler('lw', [1, 2, 3, 4]))
        ax1.xaxis.set_minor_locator(dates.MonthLocator(interval=3))
        ax1.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
        ax1.xaxis.set_major_locator(dates.YearLocator())
        ax1.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
        
        # origCols = [col for col in df.columns if col.startswith('orig_')]

        for col in df.columns:
            # if we're looking at this year (current) contract, let's plot a thick/black line
            # with a vertical/horizontal crosshair to make it easy to look at
            if(col == '{0}'.format(get_most_recent_year_column_name(df))) :
                ax1.plot(df[col].rolling(window=7, min_periods=7).mean(), label=col, color='black', lineWidth=1.5)
            # normal case is to display a thin line for historical years
            else :
                ax1.plot(df[col].rolling(window=7, min_periods=7).mean(), label='{0}'.format(col), lineWidth=1.0)
        
        ax1.grid(b=True, which='major', color='k', linewidth=1.0, linestyle='dashed')
        ax1.grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')

        ax1.set_title('{0} - {1}'.format(nearContract, farContractName))
        plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')

        j+=1

    #plt.suptitle('{0} Data'.format(nearContract))
    
    plt.tight_layout()
    plt.show()


def plot_single_historical_subplot(subplot, df, near, far):
    # These are the "Tableau 20" colors as RGB.    
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
                (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
                (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
                (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
                (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
    
    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
    for i in range(len(tableau20)):    
        r, g, b = tableau20[i]    
        tableau20[i] = (r / 255., g / 255., b / 255.) 
    
    subplot.set_prop_cycle(cycler('color', tableau20) + 
        (4 * cycler('marker', ['^', 'H', 'p', 'v', '*'])))

    ###########
    # plot shifted data with the mean
    ###########
    shiftedCols = [col for col in df.columns]
    
    subplot.xaxis.set_major_locator(dates.MonthLocator(interval=1))
    #subplot.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos: get_month_label(x)))
    subplot.xaxis.set_major_formatter(dates.DateFormatter('%b-01'))
    
    subplot.xaxis.set_minor_locator(dates.DayLocator(bymonthday=[15], interval=1))
    subplot.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
    
    currYearColName = get_most_recent_year_column_name(df)
    for i, c in enumerate(shiftedCols):
        l = None
        if(c == currYearColName):
            subplot.plot(df[c], label=c, linewidth=2.5, color='black', markevery=100)
            subplot.axvline(df[c].last_valid_index(), color='blue', linewidth=1.75)
            subplot.axhline(df[c][df[c].last_valid_index()], color='blue', linewidth=1.75)
        else:
            subplot.plot(df[c], label=c, linewidth=1, markevery=14+(2*i))
        
    # calculate the mean for all years (minus the current contract) and plot it
    cols = [col for col in shiftedCols if col not in [currYearColName]]
    df['mean'] = df[cols].mean(axis=1)
    
    df['99per'] = df[cols].apply(lambda x: np.nanpercentile(x, 99), axis=1)
    df['75per'] = df[cols].apply(lambda x: np.nanpercentile(x, 75), axis=1)
    df['25per'] = df[cols].apply(lambda x: np.nanpercentile(x, 25), axis=1)
    df['1per'] = df[cols].apply(lambda x: np.nanpercentile(x, 1), axis=1)
    
    subplot.fill_between(df.index, 
        df['75per'].rolling(window=1, min_periods=1).mean(), 
        df['25per'].rolling(window=1, min_periods=1).mean(), 
        #color='#FFF717',
        color='#DEE2E3',
        alpha=0.65)

    subplot.plot(df['mean'], color='red', linewidth=2.5, label='AVG', markevery=100, linestyle='dashed')
    shiftedCols = [col for col in df.columns if col.startswith('orig_') == False]

    
    legend = subplot.legend(loc='lower left', ncol=2, frameon=True)
    frame = legend.get_frame()
    frame.set_facecolor('white')
    # Shrink the x-axis and place the legend on the outside
    # http://stackoverflow.com/a/4701285
    
    #box = subplot.get_position()
    #subplot.set_position([box.x0, box.y0, box.width * 0.95, box.height * 0.90])
    #legend = subplot.legend(frameon=True, loc='center left', bbox_to_anchor=(1,0.5),
    #                    fancybox=True, shadow=True, ncol=2)
    #frame = legend.get_frame()
    #frame.set_facecolor('white')

    subplot.set_title('{0} - {1}'.format(near, far))
    subplot.grid(b=True, which='major', color='k', linewidth=0.5, linestyle='dashed')
    subplot.grid(b=True, which='minor', color='k', linewidth=0.5, linestyle='dotted')
        
    # rotate major tick labels to avoid overlapping
    # http://stackoverflow.com/a/28063506
    plt.setp(subplot.get_xticklabels(), rotation=30, horizontalalignment='right')
    #plt.subplots_adjust(hspace=0.3)    # this does not seem to work with ax.set_position() above - it causes that call to not be executed
    
    
    
def plot_single_historical_comparison(df, near, far):
    plt.style.use('seaborn-colorblind')

    f1 = plt.figure(num=1, figsize=(14, 9), dpi=80)
    
    subplot = f1.add_subplot(1,1,1)
    plot_single_historical_subplot(subplot, df, near, far)
    
    plt.tight_layout()
    plt.savefig('.\output\charts\{0}-{1}_Hist_{2}.png'.format(near, far, dt.date.today().strftime('%Y-%b-%d')))
    
    plt.show()

def plot_historical_comparison(tupleList, near, selected_far_contracts):
    plt.style.use('seaborn-colorblind')
    
    f1 = plt.figure(num=1, figsize=(12, 8.2), dpi=80)
    
    j = 1
    for pair in tupleList:
        farContractName = pair[0]

        if(farContractName[2] not in selected_far_contracts):
            continue

        df = pair[1]

        subplot = f1.add_subplot(len(selected_far_contracts),1,j)
        plot_single_historical_subplot(subplot, df, near, farContractName)

        j+=1
    
    plt.tight_layout()
    plt.savefig('.\output\charts\{0}_Hist_{1}.png'.format(near, dt.date.today().strftime('%Y-%b-%d')))
    plt.show()
