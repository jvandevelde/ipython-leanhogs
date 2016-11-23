import pandas as pd

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

def print_df(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')