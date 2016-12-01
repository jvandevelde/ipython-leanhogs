from __future__ import print_function
import pandas as pd
import datetime as dt

from ipywidgets import interact, interactive, fixed
#from ipywidgets import *
import ipywidgets as widgets

from IPython.display import display

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

displayMonths = { 
    'G - February':'G', # Feb
    'J - April':'J', # Apr
    'K - May':'K', #May    
    'M - June':'M', #Jun 
    'N - July':'N', #Jul
    'Q - August':'Q', #Aug
    'V - October':'V', #Oct
    'Z - December':'Z'  #Dec 
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

def VBox(*pargs, **kwargs):
    """Displays multiple widgets vertically using the flexible box model."""
    box = widgets.Box(*pargs, **kwargs)
    box.layout.display = 'flex'
    box.layout.flex_flow = 'column'
    box.layout.align_items = 'stretch'
    return box

def HBox(*pargs, **kwargs):
    """Displays multiple widgets horizontally using the flexible box model."""
    box = widgets.Box(*pargs, **kwargs)
    box.layout.display = 'flex'
    box.layout.align_items = 'stretch'
    return box

def test():
    def on_click(b):
        print('Clicked val1:{0} val2:{1}'.format(x.value, y.value))

    newMonths = list(zip(displayMonths.keys(), displayMonths.values()))

    buttons_layout = widgets.Layout(flex='1 1 auto',
                        width='auto')     # override the default width of the button to 'auto' to let the button grow

    box_layout = widgets.Layout(display='flex',
                        #flex_flow='column',
                        align_items='stretch',
                        border='solid',
                        width='50%')



    x = widgets.Dropdown(
        options=newMonths)

    
    y = widgets.SelectMultiple(
        options=list(range(2000, dt.datetime.today().year + 1)),
        value=list(range(dt.datetime.today().year - 4, dt.datetime.today().year + 1)),
        disabled=False
    )
    y.layout.height = '260px'

    generateHistoricalBtn = widgets.Button(
        description='Generate Historical',
        disabled=False,
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        tooltip='Generate Historical',
        icon='check'
    )
    generateHistoricalBtn.on_click(on_click)
    generateHistoricalBtn.layout = buttons_layout

    generateComparison = widgets.Button(
        description='Generate Comparison',
        disabled=False,
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        tooltip='Generate Interactive',
        icon='check'
    )
    generateComparison.layout = buttons_layout

    generateInteractive = widgets.Button(
        description='Generate Comparison',
        disabled=False,
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        tooltip='Generate Interactive',
        icon='check'
    )
    generateInteractive.layout = buttons_layout
    

    items = [generateComparison, generateHistoricalBtn, generateInteractive]
    box = widgets.Box(children=items, layout=box_layout)
    display(box)

    
    
    display(x)
    display(y)
    #display(generateHistoricalBtn)
    #display(generateInteractive)
    #display(generateComparison)