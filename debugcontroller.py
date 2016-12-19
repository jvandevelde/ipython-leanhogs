import utility as util
import controller as con
import lhdata

custom_series_list = {
    '2012 and 2013':['2012','2013'], 
    '2012 - 2015':['2012','2013','2014','2015'],
    '2012 - 2016':['2012', '2012','2013','2014','2015', '2016']
}


near = 'LNV'
dfList = con.calculate(near, [2015,2016])
lhdata.plot_historical_comparison(dfList, near)
