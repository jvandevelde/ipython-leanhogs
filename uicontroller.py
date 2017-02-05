from __future__ import print_function
import datetime as dt

from ipywidgets import interact, interactive, fixed, HBox
import ipywidgets as widgets
from IPython.display import display
from IPython.display import clear_output

import cufflinks as cf
import plotly
import plotly.offline as py
import plotly.graph_objs as go

import utility as util
import controller
import lhdata

import seaborn as sns

def start(custSeriesDef):
    sns.set(font_scale=1.30)
    sns.set_style("whitegrid")

    # historical comparison - 3 rows/far contracts in a single figure
    def on_click_historical_popout(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        lhdata.plot_historical_comparison(dfList, near, sel_far_contracts)

    # historical comparison - single far contract
    def on_click_single_historical_popout(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        dfDisplay = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far][0]
        lhdata.plot_single_historical_comparison(dfDisplay, near, far)

    # historical comparison - figure per far contract, with a plot per year
    def on_click_individual_popout(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_individual_against_current(dfList, near, sel_far_contracts)

    def on_click_historical_cont_popout(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_continual_spread_set(dfList, near, sel_far_contracts)
        
    def on_click_monthly_historical_boxplot(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_monthly_seasonal_boxplot(dfList, near, sel_far_contracts)
       
    def on_click_weekly_historical_boxplot(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_weekly_seasonal_boxplot(dfList, near, sel_far_contracts)

    def on_click_historical_interactive(b):
        clear_output()
        cf.go_offline() # required to use plotly offline (no account required).
        py.init_notebook_mode() # graphs charts inline (IPython).
        
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)

        dfList = controller.calculate(near, list(multi_yr_sel.value))
        disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
        df = disp[0].dropna(how='all')
        df.iplot(kind='scatter', xTitle='Date', yTitle='Difference', title='{0}-{1}'.format(near, far), theme='henanigans', dimensions=(850,350))
        
        #cf.getThemes() # gets the full list of available themes for cufflinks/plottly

    def on_click_gen_custom_series(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)
        title = 'Custom mean {0} - {1}'.format(near, far)
        
        unique_years = list(set(x for l in list(custSeriesDef.values()) for x in l))
        
        dfList = controller.calculate(near, unique_years)
        disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
        lhdata.plot_custom_historical_series(disp[0], custSeriesDef, title)
        
    
    def on_click_gen_custom_int_series(b):
        clear_output()
        cf.go_offline() # required to use plotly offline (no account required).
        py.init_notebook_mode() # graphs charts inline (IPython).
        
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)
        title = 'Custom mean {0} - {1}'.format(near, far)
        
        unique_years = list(set(x for l in list(custSeriesDef.values()) for x in l))

        dfList = controller.calculate(near, unique_years)
        disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
        dfAvgs = lhdata.calculate_custom_historical_series(disp[0], custSeriesDef)
        dfAvgs.dropna(how='all').iplot(kind='scatter', xTitle='Date', yTitle='Difference', title=title, theme='polar', dimensions=(850,350))

        #cf.getThemes() # gets the full list of available themes for cufflinks/plottly

    def on_near_month_dropdown_change(name, old, new):
        new_far_contracts = util.regularMonthSets[new]
        
        far_month_dropdown.options = new_far_contracts
        far_month_dropdown.value = far_month_dropdown.options[0]
        
        multi_far_contract_sel.options = []
        multi_far_contract_sel.options = new_far_contracts
        multi_far_contract_sel.value = util.regularMonthSets[new]

    multi_yr_sel = widgets.SelectMultiple(
        options=list(range(1998, dt.datetime.today().year + 1)),
        value=list(range(dt.datetime.today().year - 4, dt.datetime.today().year + 1)),
        width='100px')
    multi_yr_sel.layout.height = '250px'


    gen_hist_popout_btn = widgets.Button(
        description='#1 - Hist. Comparison',
        tooltip='Historical Comparison for all far contracts selected',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_popout_btn.on_click(on_click_historical_popout)
    
    gen_single_hist_popout_btn = widgets.Button(
        description='#2 - 1x Hist. Comparison',
        tooltip='Historical Comparison with only 1 far contract shown',
        width='250px',
        button_style='warning', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_single_hist_popout_btn.on_click(on_click_single_historical_popout)

    gen_hist_cont_popout_btn = widgets.Button(
        description='#3 - Continous Series',
        tooltip='Shows the spread over time without overlay',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_cont_popout_btn.on_click(on_click_historical_cont_popout)

    gen_hist_monthly_boxplot_popout_btn = widgets.Button(
        description='#5 - Monthly Boxplot Stats',
        tooltip='Show monthly stats for selected years',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_monthly_boxplot_popout_btn.on_click(on_click_monthly_historical_boxplot)

    gen_hist_weekly_boxplot_popout_btn = widgets.Button(
        description='#7 - Weekly Boxplot Stats',
        tooltip='Show weekly stats for selected years',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_weekly_boxplot_popout_btn.on_click(on_click_weekly_historical_boxplot)

    gen_indvidual_popout_btn = widgets.Button(
        description='#9 - Individuals',
        tooltip='Show each year and contract in it''s own plot',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_indvidual_popout_btn.on_click(on_click_individual_popout)

    gen_custom_series_btn = widgets.Button(
        description='#4 - Custom series',
        tooltip='Compare the mean of each entered custom series against each other',
        width='250px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_custom_series_btn.on_click(on_click_gen_custom_series)

    gen_custom_int_series_btn = widgets.Button(
        description='#6 - Custom series (Interactive)',
        tooltip='Compare custom series',
        width='250px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_custom_int_series_btn.on_click(on_click_gen_custom_int_series)

    gen_hist_interactive_btn = widgets.Button(
        description='#8 - Single Far (Interactive)',
        tooltip='Show a single spread interactively',
        width='250px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_interactive_btn.on_click(on_click_historical_interactive)

    newMonths = list(zip(util.displayMonths.keys(), util.displayMonths.values()))
    near_month_dropdown = widgets.Dropdown(options=newMonths, width='120px', height='30px')
    near_month_dropdown.on_trait_change(on_near_month_dropdown_change, 'value')
    
    curr_near_month = near_month_dropdown.value
    multi_far_contract_sel = widgets.SelectMultiple(
        options=util.regularMonthSets[curr_near_month],
        value=util.regularMonthSets[curr_near_month],
        width='220px')
    multi_far_contract_sel.layout.height = '90px'


    dd_cont1 = widgets.HBox(children=[widgets.Label('Near Contract:'), 
        near_month_dropdown])
    
    far_month_dropdown = widgets.Dropdown(options=util.regularMonthSets[near_month_dropdown.value], width='120px', height='30px')
    
    dd_cont2 = widgets.HBox(children=[widgets.Label('Far Contract:'), 
       far_month_dropdown])
    
    btns1 = [dd_cont1, gen_hist_popout_btn, gen_hist_cont_popout_btn, gen_hist_monthly_boxplot_popout_btn, gen_hist_weekly_boxplot_popout_btn, gen_indvidual_popout_btn, multi_far_contract_sel]
    btns2 = [dd_cont2, gen_single_hist_popout_btn, gen_custom_series_btn, gen_custom_int_series_btn, gen_hist_interactive_btn]
    
    v_col1 = widgets.VBox(children=[multi_yr_sel])
    v_col2 = widgets.VBox(children=btns1)
    v_col3 = widgets.VBox(children=btns2)
    
    h_cont = widgets.HBox(children=[v_col1, v_col2, v_col3])

    # display the arranged controls
    display(h_cont)

    # define some helpers to select the last n years
    year = dt.datetime.today().year
    def on_click_sel_last_five_yrs(b):
        last_five = [x for x in multi_yr_sel.options if x > year - 5]
        multi_yr_sel.value = last_five
    def on_click_sel_last_nine_yrs(b):
        last_nine = [x for x in multi_yr_sel.options if x > year - 8]
        multi_yr_sel.value = last_nine
    def on_click_sel_last_fifteen_yrs(b):
        last_fifteen = [x for x in multi_yr_sel.options if x > year - 15]
        multi_yr_sel.value = last_fifteen
    
    btn_sel_last_five_yrs = widgets.Button(
        description='Five',
        width='80px',
        button_style='info' #'success', 'info', 'warning', 'danger' or ''
        )
    btn_sel_last_five_yrs.on_click(on_click_sel_last_five_yrs)

    btn_sel_last_nine_yrs = widgets.Button(
        description='Nine',
        width='80px',
        button_style='info' #'success', 'info', 'warning', 'danger' or ''
        )
    btn_sel_last_nine_yrs.on_click(on_click_sel_last_nine_yrs)

    btn_sel_last_fifteen_yrs = widgets.Button(
        description='Fifteen',
        width='80px',
        button_style='info' #'success', 'info', 'warning', 'danger' or ''
        )
    btn_sel_last_fifteen_yrs.on_click(on_click_sel_last_fifteen_yrs)
    
    h_sel_cont = widgets.HBox(children=[btn_sel_last_five_yrs, btn_sel_last_nine_yrs, btn_sel_last_fifteen_yrs])

    # display the arranged controls
    display(h_sel_cont)