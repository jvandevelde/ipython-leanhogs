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


def start(custSeriesDef):
    def on_click_historical_popout(b):
        clear_output()
        print('Clicked val1:{0} val2:{1}'.format(near_month_dropdown.value, multi_yr_sel.value))
        near = 'LN{0}'.format(near_month_dropdown.value)
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        lhdata.plot_historical_comparison(dfList, near)
        lhdata.plot_continual_spread_set(dfList, near)

    def on_click_historical_interactive(b):
        clear_output()
        cf.go_offline() # required to use plotly offline (no account required).
        py.init_notebook_mode() # graphs charts inline (IPython).
        
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)

        dfList = controller.calculate(near, list(multi_yr_sel.value))
        disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
        df = disp[0].dropna(how='all')
        df.iplot(kind='scatter',xTitle='Date',yTitle='Difference',title='{0}-{1}'.format(near, far), theme='henanigans', dimensions=(1000,500))
        cf.getThemes()

    def on_click_gen_custom_series(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)
        
        dfList = controller.calculate(near, list(multi_yr_sel.value))
        disp = [dfHistorical for (farContract, dfHistorical, dfContinuous) in dfList if farContract == far]
        dfAvgs = lhdata.plot_custom_historical_series(disp[0], custSeriesDef, '2017')
        
        return dfAvgs

    def on_click_gen_custom_int_series(b):
        clear_output()
        near = 'LN{0}'.format(near_month_dropdown.value)
        far = 'LN{0}'.format(far_month_dropdown.value)

        dfAvgs = on_click_gen_custom_series(b)
        dfAvgs.dropna(how='all').iplot(kind='scatter', xTitle='Date', yTitle='Difference', title='{0}-{1}'.format(near,far), theme='polar', dimensions=(900,500))

    def on_near_month_dropdown_change(name, old, new):
        far_month_dropdown.options = util.regularMonthSets[new]

    newMonths = list(zip(util.displayMonths.keys(), util.displayMonths.values()))

    multi_yr_sel = widgets.SelectMultiple(
        options=list(range(2000, dt.datetime.today().year + 1)),
        value=list(range(dt.datetime.today().year - 4, dt.datetime.today().year + 1)),
        width='100px')
    multi_yr_sel.layout.height = '250px'


    gen_hist_popout_btn = widgets.Button(
        description='Generate All Externally',
        tooltip='Will open multiple windows with figures',
        width='220px',
        button_style='success', #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_popout_btn.on_click(on_click_historical_popout)

    gen_hist_interactive_btn = widgets.Button(
        description='Show Single Interactive',
        tooltip='Show Near-Far inline',
        width='220px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_hist_interactive_btn.on_click(on_click_historical_interactive)

    gen_custom_series_btn = widgets.Button(
        description='Compare custom series',
        tooltip='Compare custom series',
        width='220px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_custom_series_btn.on_click(on_click_gen_custom_series)

    gen_custom_int_series_btn = widgets.Button(
        description='Compare custom series (Interactive)',
        tooltip='Compare custom series',
        width='220px',
        button_style='warning' #'success', 'info', 'warning', 'danger' or ''
        )
    gen_custom_int_series_btn.on_click(on_click_gen_custom_int_series)

    near_month_dropdown = widgets.Dropdown(options=newMonths, width='120px', height='30px')
    near_month_dropdown.on_trait_change(on_near_month_dropdown_change, 'value')

    dd_cont1 = widgets.HBox(children=[widgets.Label('Near Contract:'), 
        near_month_dropdown])
    
    far_month_dropdown = widgets.Dropdown(options=util.regularMonthSets[near_month_dropdown.value], width='120px', height='30px')
    
    dd_cont2 = widgets.HBox(children=[widgets.Label('Far Contract:'), 
       far_month_dropdown])
    
    btns1 = [dd_cont1, gen_hist_popout_btn]
    btns2 = [dd_cont2, gen_hist_interactive_btn, gen_custom_series_btn, gen_custom_int_series_btn]
    v_col1 = widgets.VBox(children=[multi_yr_sel])
    v_col2 = widgets.VBox(children=btns1)
    v_col3 = widgets.VBox(children=btns2)
    h_cont = widgets.HBox(children=[v_col1, v_col2, v_col3])

    display(h_cont)

    # define some helpers to select the last n years
    def on_click_sel_last_five_yrs(b):
        multi_yr_sel.value=list(range(dt.datetime.today().year - 4, dt.datetime.today().year + 1)),
    def on_click_sel_last_nine_yrs(b):
        multi_yr_sel.value=list(range(dt.datetime.today().year - 8, dt.datetime.today().year + 1)),
    def on_click_sel_last_fifteen_yrs(b):
        multi_yr_sel.value=list(range(dt.datetime.today().year - 14, dt.datetime.today().year + 1)),
    


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

    display(h_sel_cont)