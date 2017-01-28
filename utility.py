import collections
import pandas as pd
import datetime as dt

allMonths = { 
    'X1':1, #Jan
    'G':2, # Feb
    'X2':3,
    'J':4, # Apr
    'K':5, #May    
    'M':6, #Jun 
    'N':7, #Jul
    'Q':8, #Aug
    'X3':9,
    'V':10, #Oct
    'X4':11,
    'Z':12  #Dec 
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

displayMonths = collections.OrderedDict() 
displayMonths['G - February '] = 'G'
displayMonths['J - April'] = 'J'
displayMonths['K - May'] = 'K'    
displayMonths['M - June'] = 'M' 
displayMonths['N - July'] = 'N'
displayMonths['Q - August'] = 'Q'
displayMonths['V - October'] = 'V'
displayMonths['Z - December'] = 'Z' 


regularMonthSets = {
    'G':['J','K','M','N'],
    'J':['K','M','N','Q'],
    'K':['M','N','Q','V'],
    'M':['N','Q','V','Z'],
    'N':['Q','V','Z','G'],
    'Q':['V','Z','G','J'],
    'V':['Z','G','J','K'],
    'Z':['G','J','K','M']
}

def print_df(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    fourth_jan = dt.date(iso_year, 1, 4)
    _, fourth_jan_week, fourth_jan_day = fourth_jan.isocalendar()
    return fourth_jan + dt.timedelta(days=iso_day-fourth_jan_day, weeks=iso_week-fourth_jan_week)
    
def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (dt.date(d.year + years, 1, 1) - dt.date(d.year, 1, 1))