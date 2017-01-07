import collections
import pandas as pd

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
    'G':['J','K','M'],
    'J':['K','M','N'],
    'K':['M','N','Q'],
    'M':['N','Q','V'],
    'N':['Q','V','Z'],
    'Q':['V','Z','G'],
    'V':['Z','G','J'],
    'Z':['G','J','K']
}

def print_df(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
    