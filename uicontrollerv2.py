from __future__ import print_function
import datetime as dt
import os
import ipywidgets as widgets
from IPython.display import display, HTML

import utility as util
import controller
import lhdata
import butterfly
import dataManager as dm

from exceptions import ContractException
from PyQt5.QtWidgets import QFileDialog, QApplication
import seaborn as sns


def start(custSeriesDef):
    sns.set(font_scale=1.30)
    sns.set_style('whitegrid')
    output_dir = './output/charts/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # -- Inject custom CSS --
    display(HTML('''
<style>
  .lh-panel {
    background: #edf0f5;
    border-radius: 12px;
    padding: 20px 24px;
    color: #2d3148;
    font-family: Segoe UI, sans-serif;
    border: 1px solid #c4c9d8;
  }
  .lh-section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #7a8099;
    margin-bottom: 6px;
    margin-top: 0px;
  }
  .lh-divider {
    border: none;
    border-top: 1px solid #c4c9d8;
    margin: 14px 0;
  }
  .lh-bfly-col {
    background: #e2e6ef;
    border: 1px solid #c4c9d8;
    border-radius: 10px;
    padding: 14px 16px;
  }
  .lh-yr-sel select {
    background: #f8f9fb !important;
    color: #2d3148 !important;
    border: 1px solid #c4c9d8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-family: Segoe UI, sans-serif !important;
  }
  .lh-dropdown select {
    background: #f8f9fb !important;
    color: #2d3148 !important;
    border: 1px solid #c4c9d8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-family: Segoe UI, sans-serif !important;
  }
  .lh-dropdown-inset select {
    background: #f8f9fb !important;
    color: #2d3148 !important;
    border: 1px solid #c4c9d8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-family: Segoe UI, sans-serif !important;
  }
  .lh-text-input input {
    background: #f8f9fb !important;
    color: #2d3148 !important;
    border: 1px solid #c4c9d8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-family: Segoe UI, sans-serif !important;
    padding: 6px 10px !important;
  }
  .lh-btn-browse, .lh-btn-browse button {
    background: #2e3250 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
  }
  .lh-btn-yr, .lh-btn-yr button {
    background: #2e3250 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    margin-right: 4px !important;
  }
  .lh-btn-chart, .lh-btn-chart button {
    background: #2e3250 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
    width: 100% !important;
    text-align: left !important;
  }
  .lh-btn-bfly-pre, .lh-btn-bfly-pre button {
    background: #2e3250 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    width: 100% !important;
  }
  .lh-btn-bfly-cust, .lh-btn-bfly-cust button {
    background: #2e3250 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    width: 100% !important;
  }
  .lh-far-sel select {
    background: #f8f9fb !important;
    color: #2d3148 !important;
    border: 1px solid #c4c9d8 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
  }
  .lh-slider .widget-label {
    color: #2d3148 !important;
    font-size: 12px !important;
  }
</style>
    '''))

    # -- Options: (display_label, single_letter_key) --
    month_opts = list(zip(util.displayMonths.keys(), util.displayMonths.values()))
    butterfly_options = list(util.commonButterflies.keys())
    today_year = dt.datetime.today().year

    # -- STATUS OUTPUT --
    status_out = widgets.Output()

    def set_status(msg, color='#1a7a35'):
        status_out.clear_output()
        with status_out:
            display(HTML('<span style="font-size:13px;font-family:Segoe UI,sans-serif;color:{0};">{1}</span>'.format(color, msg)))

    # -- DATA FILE ROW --
    data_file_input = widgets.Text(
        value=dm.DATA_FILE,
        placeholder='Path to settlement data Excel file',
        layout=widgets.Layout(width='420px')
    )
    data_file_input.add_class('lh-text-input')

    browse_btn = widgets.Button(description='Browse...', layout=widgets.Layout(width='90px'))
    browse_btn.add_class('lh-btn-browse')
    browse_btn.style.button_color = '#2e3250'

    def on_browse(b):
        app = QApplication.instance() or QApplication([])
        path, _ = QFileDialog.getOpenFileName(None, 'Select Settlement Data File', '', 'Excel Files (*.xlsx *.xls)')
        if path:
            data_file_input.value = path
            set_status('Data file set: {0}'.format(path))

    browse_btn.on_click(on_browse)

    file_label = widgets.HTML('<span class="lh-section-title">Data File</span>')
    file_row = widgets.VBox([
        file_label,
        widgets.HBox([data_file_input, browse_btn], layout=widgets.Layout(align_items='center'))
    ])

    # -- YEAR SELECTOR + QUICK SELECT --
    yr_options = list(range(1998, today_year + 1))
    yr_sel = widgets.SelectMultiple(
        options=yr_options,
        value=list(range(today_year - 4, today_year + 1)),
        layout=widgets.Layout(width='100px', height='250px')
    )
    yr_sel.add_class('lh-yr-sel')

    btn_five    = widgets.Button(description='5 Yrs',  layout=widgets.Layout(width='68px'))
    btn_nine    = widgets.Button(description='9 Yrs',  layout=widgets.Layout(width='68px'))
    btn_fifteen = widgets.Button(description='15 Yrs', layout=widgets.Layout(width='68px'))
    for _b in [btn_five, btn_nine, btn_fifteen]:
        _b.add_class('lh-btn-yr')
        _b.style.button_color = '#2e3250'

    def on_five(b):
        yr_sel.value = [x for x in yr_sel.options if x > today_year - 5]
    def on_nine(b):
        yr_sel.value = [x for x in yr_sel.options if x > today_year - 8]
    def on_fifteen(b):
        yr_sel.value = [x for x in yr_sel.options if x > today_year - 15]

    btn_five.on_click(on_five)
    btn_nine.on_click(on_nine)
    btn_fifteen.on_click(on_fifteen)

    yr_label     = widgets.HTML('<span class="lh-section-title">Years</span>')
    yr_quick_row = widgets.HBox([btn_five, btn_nine, btn_fifteen], layout=widgets.Layout(margin='6px 0 0 0'))
    yr_col       = widgets.VBox([yr_label, yr_sel, yr_quick_row])

    # -- NEAR / FAR CONTRACT SELECTORS --
    near_dd = widgets.Dropdown(
        options=month_opts,
        value='G',
        layout=widgets.Layout(width='160px')
    )
    near_dd.add_class('lh-dropdown')

    far_sel = widgets.SelectMultiple(
        options=util.regularMonthSets['G'],
        value=util.regularMonthSets['G'],
        layout=widgets.Layout(width='120px', height='120px')
    )
    far_sel.add_class('lh-far-sel')

    def on_near_change(change):
        new_opts = util.regularMonthSets[change['new']]
        far_sel.options = new_opts
        far_sel.value = new_opts

    near_dd.observe(on_near_change, names='value')

    near_label   = widgets.HTML('<span class="lh-section-title">Near Contract</span>')
    far_label    = widgets.HTML('<span class="lh-section-title">Far Contracts</span>')
    contract_col = widgets.VBox([near_label, near_dd, far_label, far_sel], layout=widgets.Layout(margin='0 0 0 16px'))

    # -- HELPERS --
    def get_near():
        return 'LN{0}'.format(near_dd.value)

    def get_far_list():
        sel = list(far_sel.value)
        if len(sel) == 0:
            sel = util.regularMonthSets[near_dd.value]
        return sel

    def load_data():
        dm.DATA_FILE = data_file_input.value
        near = get_near()
        yrs = list(yr_sel.value)
        set_status('Loading data...', color='#b54f00')
        dfList = controller.calculate(near, yrs)
        set_status('Ready - {0} years loaded.'.format(len(yrs)), color='#1a7a35')
        return near, dfList

    # -- CHART CALLBACKS --
    def on_click_historical(b):
        try:
            near, dfList = load_data()
            lhdata.plot_historical_comparison(dfList, near, get_far_list())
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_continuous(b):
        try:
            near, dfList = load_data()
            lhdata.plot_continual_spread_set(dfList, near, get_far_list())
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_monthly(b):
        try:
            near, dfList = load_data()
            lhdata.plot_monthly_seasonal_boxplot(dfList, near, get_far_list())
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_weekly(b):
        try:
            near, dfList = load_data()
            lhdata.plot_weekly_seasonal_boxplot(dfList, near, get_far_list())
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_individual(b):
        try:
            near, dfList = load_data()
            lhdata.plot_individual_against_current(dfList, near, get_far_list())
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_custom_series(b):
        try:
            dm.DATA_FILE = data_file_input.value
            near = get_near()
            unique_years = list(set(x for lst in list(custSeriesDef.values()) for x in lst))
            set_status('Generating custom series...', color='#b54f00')
            dfList = controller.calculate(near, unique_years)
            for fc in get_far_list():
                far = 'LN{0}'.format(fc)
                title = 'Custom Means {0} - {1}'.format(near, far)
                disp = [dfH for (farC, dfH, _) in dfList if farC == far]
                if disp:
                    lhdata.plot_custom_historical_series(disp[0], custSeriesDef, title)
            set_status('Custom series done.', color='#1a7a35')
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    # -- CHART BUTTONS --
    btn_hist    = widgets.Button(description='1 - Historical Spreads',  tooltip='Historical comparison for selected far contracts', layout=widgets.Layout(width='210px'))
    btn_cont    = widgets.Button(description='2 - Continuous Spread',   tooltip='Shows the spread over time without overlay',       layout=widgets.Layout(width='210px'))
    btn_monthly = widgets.Button(description='3 - Monthly Boxplots',    tooltip='Monthly boxplot statistics for selected years',    layout=widgets.Layout(width='210px'))
    btn_weekly  = widgets.Button(description='4 - Weekly Boxplots',     tooltip='Weekly boxplot statistics for selected years',     layout=widgets.Layout(width='210px'))
    btn_indiv   = widgets.Button(description='5 - Individuals',         tooltip='Each year and contract in its own plot',           layout=widgets.Layout(width='210px'))
    btn_cseries = widgets.Button(description='6 - Custom Series',       tooltip='Compare custom series means',                     layout=widgets.Layout(width='210px'))
    for _b in [btn_hist, btn_cont, btn_monthly, btn_weekly, btn_indiv, btn_cseries]:
        _b.add_class('lh-btn-chart')
        _b.style.button_color = '#2e3250'

    btn_hist.on_click(on_click_historical)
    btn_cont.on_click(on_click_continuous)
    btn_monthly.on_click(on_click_monthly)
    btn_weekly.on_click(on_click_weekly)
    btn_indiv.on_click(on_click_individual)
    btn_cseries.on_click(on_click_custom_series)

    chart_label = widgets.HTML('<span class="lh-section-title">Charts</span>')
    chart_col   = widgets.VBox([chart_label, btn_hist, btn_cont, btn_monthly, btn_weekly, btn_indiv, btn_cseries],
                                layout=widgets.Layout(margin='0 0 0 16px'))

    # -- BUTTERFLY SHARED CONTROLS --
    bfly_layout_dd = widgets.Dropdown(
        options=['Regular', 'Condensed', 'Both'],
        value='Both',
        layout=widgets.Layout(width='130px')
    )
    bfly_layout_dd.add_class('lh-dropdown')

    bfly_percentile = widgets.IntRangeSlider(
        value=[25, 75], min=0, max=100, step=5,
        description='Percentile:',
        layout=widgets.Layout(width='300px')
    )
    bfly_percentile.add_class('lh-slider')

    shared_row = widgets.HBox([
        widgets.VBox([
            widgets.HTML('<span style="font-size:11px;color:#5c6278;font-weight:700;letter-spacing:1px;">LAYOUT</span>'),
            bfly_layout_dd
        ]),
        widgets.VBox([
            widgets.HTML('<span style="font-size:11px;color:#5c6278;font-weight:700;letter-spacing:1px;">PERCENTILE BAND</span>'),
            bfly_percentile
        ], layout=widgets.Layout(margin='0 0 0 20px'))
    ], layout=widgets.Layout(align_items='flex-end', margin='0 0 14px 0', overflow_x='hidden'))

    # -- BUTTERFLY: PREDEFINED COLUMN --
    PRE_W = '168px'

    bfly_predefined_dd = widgets.Dropdown(
        options=butterfly_options,
        value=butterfly_options[0],
        layout=widgets.Layout(width=PRE_W)
    )
    bfly_predefined_dd.add_class('lh-dropdown-inset')

    btn_bfly_pre = widgets.Button(
        description='Generate Predefined',
        tooltip='Generate butterfly chart using the selected preset',
        layout=widgets.Layout(width=PRE_W)
    )
    btn_bfly_pre.add_class('lh-btn-bfly-pre')
    btn_bfly_pre.style.button_color = '#2e3250'

    pre_col_inner = widgets.VBox([
        widgets.HTML('<span style="font-size:11px;color:#5c6278;font-weight:700;letter-spacing:1px;">PRESET</span>'),
        bfly_predefined_dd,
        btn_bfly_pre,
    ], layout=widgets.Layout(width='200px', padding='14px 16px', overflow_x='hidden'))
    pre_col_inner.add_class('lh-bfly-col')

    pre_col = widgets.VBox([
        widgets.HTML('<span style="font-size:13px;font-weight:700;color:#6b20c0;margin-bottom:6px;display:block;">Predefined</span>'),
        pre_col_inner,
    ], layout=widgets.Layout(overflow_x='hidden'))

    # -- BUTTERFLY: CUSTOM COLUMN --
    LEG_W = '148px'
    BTN_W = '460px'

    bfly_x_dd = widgets.Dropdown(options=month_opts, value='G', layout=widgets.Layout(width=LEG_W))
    bfly_y_dd = widgets.Dropdown(options=month_opts, value='K', layout=widgets.Layout(width=LEG_W))
    bfly_z_dd = widgets.Dropdown(options=month_opts, value='N', layout=widgets.Layout(width=LEG_W))
    for _b in [bfly_x_dd, bfly_y_dd, bfly_z_dd]:
        _b.add_class('lh-dropdown-inset')

    btn_bfly_cust = widgets.Button(
        description='Generate Custom',
        tooltip='Generate butterfly chart using the three leg contracts below',
        layout=widgets.Layout(width=BTN_W)
    )
    btn_bfly_cust.add_class('lh-btn-bfly-cust')
    btn_bfly_cust.style.button_color = '#2e3250'

    leg_row = widgets.HBox([
        widgets.VBox([widgets.HTML('<span style="font-size:11px;color:#5c6278;">LEG X</span>'), bfly_x_dd]),
        widgets.VBox([widgets.HTML('<span style="font-size:11px;color:#5c6278;">LEG Y</span>'), bfly_y_dd],
                     layout=widgets.Layout(margin='0 0 0 8px')),
        widgets.VBox([widgets.HTML('<span style="font-size:11px;color:#5c6278;">LEG Z</span>'), bfly_z_dd],
                     layout=widgets.Layout(margin='0 0 0 8px')),
    ], layout=widgets.Layout(align_items='flex-end', overflow_x='hidden'))

    cust_col_inner = widgets.VBox([
        leg_row,
        btn_bfly_cust,
    ], layout=widgets.Layout(padding='14px 16px', overflow_x='hidden'))
    cust_col_inner.add_class('lh-bfly-col')

    cust_col = widgets.VBox([
        widgets.HTML('<span style="font-size:13px;font-weight:700;color:#a06010;margin-bottom:6px;display:block;">Custom</span>'),
        cust_col_inner,
    ], layout=widgets.Layout(overflow_x='hidden'))

    # -- BUTTERFLY CALLBACKS --
    def on_click_bfly_predefined(b):
        try:
            dm.DATA_FILE = data_file_input.value
            selected_tuple = util.commonButterflies[bfly_predefined_dd.value]
            layout = bfly_layout_dd.value
            q_override = bfly_percentile.value
            cx = 'LN{0}'.format(selected_tuple[0])
            cy = 'LN{0}'.format(selected_tuple[1])
            cz = 'LN{0}'.format(selected_tuple[2])
            set_status('Generating butterfly {0}...'.format(bfly_predefined_dd.value), color='#5c1fa0')
            butterfly.create_chart((cx, cy, cz), list(yr_sel.value), layout, q_override)
            set_status('Butterfly {0} done.'.format(bfly_predefined_dd.value), color='#1a7a35')
        except ContractException as e:
            set_status('Error: {0}'.format(e.args[0]), color='#c0152a')
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    def on_click_bfly_custom(b):
        try:
            dm.DATA_FILE = data_file_input.value
            layout = bfly_layout_dd.value
            q_override = bfly_percentile.value
            cx = 'LN{0}'.format(bfly_x_dd.value)
            cy = 'LN{0}'.format(bfly_y_dd.value)
            cz = 'LN{0}'.format(bfly_z_dd.value)
            set_status('Generating custom butterfly {0}-{1}-{2}...'.format(
                bfly_x_dd.value, bfly_y_dd.value, bfly_z_dd.value), color='#8a5e00')
            butterfly.create_chart((cx, cy, cz), list(yr_sel.value), layout, q_override)
            set_status('Custom butterfly done.', color='#1a7a35')
        except ContractException as e:
            set_status('Error: {0}'.format(e.args[0]), color='#c0152a')
        except Exception as e:
            set_status('Error: {0}'.format(str(e)), color='#c0152a')

    btn_bfly_pre.on_click(on_click_bfly_predefined)
    btn_bfly_cust.on_click(on_click_bfly_custom)

    # -- ASSEMBLE BUTTERFLY SECTION --
    bfly_label   = widgets.HTML('<span class="lh-section-title">Butterfly Spreads</span>')
    bfly_cols    = widgets.HBox(
        [pre_col, cust_col],
        layout=widgets.Layout(grid_gap='20px', align_items='flex-start', overflow_x='hidden')
    )
    bfly_section = widgets.VBox(
        [bfly_label, shared_row, bfly_cols],
        layout=widgets.Layout(overflow_x='hidden')
    )

    # -- ASSEMBLE MAIN LAYOUT --
    divider = widgets.HTML('<hr class="lh-divider"/>')

    top_row = widgets.HBox([yr_col, contract_col, chart_col],
                            layout=widgets.Layout(align_items='flex-start'))

    main_box = widgets.VBox([
        widgets.HTML('<div style="font-size:16px;font-weight:700;color:#2d3148;margin-bottom:10px;">Lean Hogs Analysis</div>'),
        file_row,
        divider,
        top_row,
        divider,
        bfly_section,
        divider,
        widgets.HTML('<span class="lh-section-title">Status</span>'),
        status_out,
    ], layout=widgets.Layout(padding='20px', border='1px solid #313244', overflow_x='hidden'))

    main_box.add_class('lh-panel')
    display(main_box)
    set_status('Ready. Select years and contracts, then click a chart button.')