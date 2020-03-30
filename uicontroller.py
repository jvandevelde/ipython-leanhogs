from __future__ import print_function
import datetime as dt
import os, sys

from ipywidgets import interact, interactive, fixed, HBox
import ipywidgets as widgets
from IPython.display import display
from IPython.display import clear_output

import utility as util
import controller
import lhdata
import butterfly

import seaborn as sns
from exceptions import ContractException

def start(custSeriesDef):
    sns.set(font_scale=1.30)
    sns.set_style('whitegrid')
    output_dir = './output/charts/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # historical comparison - 3 rows/far contracts in a single figure
    def on_click_historical_popout(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        lhdata.plot_historical_comparison(dfList, near, sel_far_contracts)

        # To plot a single far contract
        #dfDisplay = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far][0]
        #lhdata.plot_single_historical_comparison(dfDisplay, near, far)    

    # historical comparison - figure per far contract, with a plot per year
    def on_click_individual_popout(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_individual_against_current(dfList, near, sel_far_contracts)

    def on_click_historical_cont_popout(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_continual_spread_set(dfList, near, sel_far_contracts)

    def on_click_generate_butterfly(b):
        #clear_output()
        
        layout = butterfly_chart_layout_sel.value
        quartile_overrides = butterfly_condensed_range_slider.value

        contract_x = "LN{0}".format(custom_butterfly_contract_x.value)
        contract_y = "LN{0}".format(custom_butterfly_contract_y.value)
        contract_z = "LN{0}".format(custom_butterfly_contract_z.value)
        contractsTuple = (contract_x, contract_y, contract_z)
        
        try:
            butterfly.create_chart(contractsTuple, list(multi_yr_sel.value), layout, quartile_overrides)
        except ContractException as e:
            print("Error: ", e.args[0])
            
    def on_click_generate_predefined_butterfly(b):
        
        selected_tuple = util.commonButterflies[predefined_butterfly_sel.value]
        
        layout = butterfly_chart_layout_sel.value
        quartile_overrides = butterfly_condensed_range_slider.value

        contract_x = "LN{0}".format(selected_tuple[0])
        contract_y = "LN{0}".format(selected_tuple[1])
        contract_z = "LN{0}".format(selected_tuple[2])
        contractsTuple = (contract_x, contract_y, contract_z)
        
        try:
            butterfly.create_chart(contractsTuple, list(multi_yr_sel.value), layout, quartile_overrides)
        except ContractException as e:
            print("Error: ", e.args[0])

    def on_click_monthly_historical_boxplot(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_monthly_seasonal_boxplot(dfList, near, sel_far_contracts)
       
    def on_click_weekly_historical_boxplot(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        lhdata.plot_weekly_seasonal_boxplot(dfList, near, sel_far_contracts)

    def on_click_gen_custom_series(b):
        #clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        
        unique_years = list(set(x for l in list(custSeriesDef.values()) for x in l))
        
        dfList = controller.calculate(near, unique_years)
        
        sel_far_contracts = list(multi_far_contract_sel.value)
        if(len(sel_far_contracts) == 0):
            sel_far_contracts = util.regularMonthSets[near_month_dropdown.value]
        
        for far_contract in sel_far_contracts:
            far = 'LN{0}'.format(far_contract)
            title = 'Custom Means {0} - {1}'.format(near, far)
            disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
            lhdata.plot_custom_historical_series(disp[0], custSeriesDef, title)
        
    def on_near_month_dropdown_change(name, old, new):
        new_far_contracts = util.regularMonthSets[new]
        
        multi_far_contract_sel.options = []
        multi_far_contract_sel.options = new_far_contracts
        multi_far_contract_sel.value = util.regularMonthSets[new]

  
    multi_yr_sel = widgets.SelectMultiple(
        options=list(range(1998, dt.datetime.today().year + 1)),
        value=list(range(dt.datetime.today().year - 4, dt.datetime.today().year + 1)),
        width='100px')
    multi_yr_sel.layout.height = '300px'


    gen_hist_popout_btn = widgets.Button(
        description='#1 - Historical Spreads',
        tooltip='Historical Comparison for selected far contracts',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_popout_btn.on_click(on_click_historical_popout)

    gen_hist_cont_popout_btn = widgets.Button(
        description='#2 - Continous Spread',
        tooltip='Shows the spread over time without overlay',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_cont_popout_btn.on_click(on_click_historical_cont_popout)

    gen_hist_monthly_boxplot_popout_btn = widgets.Button(
        description='#3 - Monthly Boxplot Statistics',
        tooltip='Show monthly stats for selected years',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_monthly_boxplot_popout_btn.on_click(on_click_monthly_historical_boxplot)

    gen_hist_weekly_boxplot_popout_btn = widgets.Button(
        description='#4 - Weekly Boxplot Statistics',
        tooltip='Show weekly stats for selected years',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_weekly_boxplot_popout_btn.on_click(on_click_weekly_historical_boxplot)

    gen_indvidual_popout_btn = widgets.Button(
        description='#5 - Individuals',
        tooltip='Show each year and contract in it''s own plot',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_indvidual_popout_btn.on_click(on_click_individual_popout)

    gen_custom_series_btn = widgets.Button(
        description='#6 - Custom series',
        tooltip='Compare the mean of each entered custom series against each other',
        width='220px',
        button_style='success' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_custom_series_btn.on_click(on_click_gen_custom_series)

    newMonths = list(zip(util.displayMonths.keys(), util.displayMonths.values()))
    near_month_dropdown = widgets.Dropdown(options=newMonths, width='150px', height='30px')
    near_month_dropdown.on_trait_change(on_near_month_dropdown_change, 'value')
    
    curr_near_month = near_month_dropdown.value
    multi_far_contract_sel = widgets.SelectMultiple(
        options=util.regularMonthSets[curr_near_month],
        value=util.regularMonthSets[curr_near_month],
        width='150px')
    multi_far_contract_sel.layout.height = '90px'

    near_dropdown_container = widgets.VBox(children=[
        widgets.Label('Near Contract'), 
        near_month_dropdown])
    far_select_container = widgets.VBox(children=[
        widgets.Label('Far Contracts'),
        multi_far_contract_sel])
    
    btns = [gen_hist_popout_btn, 
            gen_hist_cont_popout_btn,
            gen_hist_monthly_boxplot_popout_btn, 
            gen_hist_weekly_boxplot_popout_btn, 
            gen_indvidual_popout_btn,
            gen_custom_series_btn]
    
    v_col1 = widgets.VBox(children=[multi_yr_sel])
    v_col2 = widgets.VBox(children=[near_dropdown_container, far_select_container])
    v_col3 = widgets.VBox(children=btns)
    
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


    # BUTTERFLY UI

    months = list(zip(util.displayMonths.keys(), util.displayMonths.values()))
    
    predefined_butterflies = list(util.commonButterflies.keys())
    
    predefined_butterfly_sel = widgets.Select(
        options=predefined_butterflies,
        value=predefined_butterflies[0],
        width='150px')
    predefined_butterfly_sel.layout.height = '190px'
    


    butterfly_chart_layout_sel = widgets.Select(
        options=['Regular', 'Condensed', 'Both'],
        value='Both',
        width='125px')
    butterfly_chart_layout_sel.layout.height = '60px'

    butterfly_condensed_range_slider = widgets.IntRangeSlider(
        value=[25, 75],
        min=0,
        max=100,
        step=5,
        description='Percentile',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
    )

    generate_predefined_butterfly_btn = widgets.Button(
        description='<- Predefined',
        tooltip='Generates the selected/predefined Butterfly',
        width='300px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
    )
    generate_predefined_butterfly_btn.on_click(on_click_generate_predefined_butterfly)
    
    
    custom_butterfly_contract_x = widgets.Dropdown(options=months, width='150px', height='30px')
    custom_butterfly_contract_y = widgets.Dropdown(options=months, width='150px', height='30px')
    custom_butterfly_contract_z = widgets.Dropdown(options=months, width='150px', height='30px')
    
    contract_x_field = widgets.VBox(children=[
        widgets.Label('Butterfly X'), 
        custom_butterfly_contract_x])    
    contract_y_field = widgets.VBox(children=[
        widgets.Label('Butterfly Z'), 
        custom_butterfly_contract_y])    
    contract_z_field = widgets.VBox(children=[
        widgets.Label('Butterfly Z'), 
        custom_butterfly_contract_z])    
    
    generate_custom_butterfly_btn = widgets.Button(
        description='Custom Sel ->',
        tooltip='Generates a custom Butterfly',
        width='320px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    generate_custom_butterfly_btn.on_click(on_click_generate_butterfly)

    
    butterfly_buttons_horz_container = widgets.HBox(children=[generate_predefined_butterfly_btn, generate_custom_butterfly_btn])
    butterfly_options_vert_container = widgets.VBox(children=[butterfly_chart_layout_sel, butterfly_condensed_range_slider, butterfly_buttons_horz_container])
    custom_butterfly_month_vert_container = widgets.VBox(children=[contract_x_field, contract_y_field, contract_z_field])
    main_container = widgets.HBox(children=[predefined_butterfly_sel, butterfly_options_vert_container, custom_butterfly_month_vert_container])
    
    display(main_container)
