#!/mesonet/python/bin/python
"""
Gonna try to make something that can plot most anything under the moon for the COOP 
data, watch me fail

-  seasonal temperatures, ex: summer daily max. temperature
-  seasonal percipitation, ex: summer annual precip.

"""
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'

import cgi
import matplotlib
matplotlib.use( 'Agg' )
matplotlib.rcParams['font.sans-serif'] = 'Arial'
matplotlib.rcParams['font.family'] = 'sans-serif'
from matplotlib import pyplot as plt
import iemdb
import numpy
import mx.DateTime
import network
from scipy import stats

META = {
 'rain_days': {
    'title': 'Station Average Number of Days of 1.25" Precipitation',
    'ylabel': 'Number of Days',
    'xlabel': 'Year', 
    'func': '',
    'month_bounds': '', 
    'valid_offset': '',        
  }, 
 'annual_sum_precip': {
    'title': 'Annual Precipitation (rain + melted snow)',
    'ylabel': 'Precipitation [inches]',
    'xlabel': 'Year', 
    'func': 'sum(precip)',
    'month_bounds': '', 
    'valid_offset': '',        
  }, 
 'annual_avg_temp': {
    'title': 'Annual Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)', 
    'month_bounds': '',   
    'valid_offset': '',     
  }, 
  'winter_avg_temp': {
    'title': 'Winter [DJF] Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)', 
    'month_bounds': 'and month in (12,1,2)',   
    'valid_offset': "- '2 month'::interval ",     
  },   
 'winter_avg_low': {
    'title': 'Winter [DJF] Average Low Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg(low)', 
    'month_bounds': 'and month in (12,1,2)',   
    'valid_offset': "- '2 month'::interval ",     
  }, 
'winter_avg_high': {
    'title': 'Winter [DJF] Average High Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg(high)', 
    'month_bounds': 'and month in (12,1,2)',   
    'valid_offset': "- '2 month'::interval ",     
  }, 
 'summer_avg_temp': {
    'title': 'Summer [JJA] Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)', 
    'month_bounds': 'and month in (6,7,8)',   
    'valid_offset': " ",     
  },  
'summer_avg_high': {
    'title': 'Summer [JJA] Average High Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg(high)', 
    'month_bounds': 'and month in (6,7,8)',   
    'valid_offset': " ",     
  }, 
  'summer_avg_low': {
    'title': 'Summer [JJA] Average Low Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg(low)', 
    'month_bounds': 'and month in (6,7,8)',   
    'valid_offset': " ",     
  }, 
 'spring_avg_temp': {
    'title': 'Spring [MAM] Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)', 
    'month_bounds': 'and month in (3,4,5)',   
    'valid_offset': " ",     
  }, 
 'fall_avg_temp': {
    'title': 'Fall [SON] Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)', 
    'month_bounds': 'and month in (9,10,11)',   
    'valid_offset': " ",     
  },   
 'frost_free': {
    'title': 'Frost Free Days',
    'ylabel': 'Days',
    'xlabel': 'Year',   
    'month_bounds': '',  
    'func': '',       
    'valid_offset': '',  
  },
 'gdd50': {
    'title': 'Growing Degree Days (1 May - 1 Oct) (base=50)',
    'ylabel': 'GDD Units [F]',
    'xlabel': 'Year',   
    'func': 'sum(gdd50(high,low))',       
    'month_bounds': 'and month in (5,6,7,8,9)',  
    'valid_offset': '',  
  }, 
  'hdd65': {
    'title': 'Heating Degree Days (1 Oct - 1 May) (base=65)',
    'ylabel': 'HDD Units [F]',
    'xlabel': 'Year',   
    'func': 'sum(hdd65(high,low))',
    'month_bounds': 'and month in (10,11,12,1,2,3,4)',   
    'valid_offset': " - '6 months'::interval ",        
  },         
}

def get_station_name(station):
    """
    Get the common name for a given station ID
    """
    nt = network.Table("%sCLIMATE" % (station[:2].upper(),))
    return nt.sts[station.upper()]['name']

def yearly_plot(ax, cfg):
    """
    Make a yearly plot of something
    """
    
    COOP = iemdb.connect('coop', bypass=True)
    ccursor = COOP.cursor()
    
    if cfg['plot_type'] == 'frost_free':
        cfg['st'] = cfg['station'][:2]
        ccursor.execute("""
        select fall.year, fall.s - spring.s from 
          (select year, max(extract(doy from day)) as s 
           from alldata_%(st)s where station = '%(station)s' and 
           month < 7 and low <= 32 and year >= %(first_year)s and 
           year <= %(last_year)s GROUP by year) as spring, 
          (select year, min(extract(doy from day)) as s 
           from alldata_%(st)s where station = '%(station)s' and 
           month > 7 and low <= 32 and year >= %(first_year)s and 
           year <= %(last_year)s GROUP by year) as fall 
         WHERE spring.year = fall.year ORDER by fall.year ASC
        """ % cfg )
    elif cfg['plot_type'] == 'rain_days':
        cfg['st'] = cfg['station'][:2]
        ccursor.execute("""
 select year as yr, avg(cnt) 
 from (select station, year, sum(case when precip >= 1.25 then 1 else 0 end) as cnt from 
 alldata_%(st)s WHERE 
 station in (select distinct station from alldata_%(st)s where year = %(first_year)s 
 and precip > 0 and year >= %(first_year)s and  year <= %(last_year)s) and
 station in (select id from stations where network = '%(st)sCLIMATE' and climate_site = '%(station)s')
 GROUP by station, year) as foo GROUP by yr ORDER by yr ASC
        """ % cfg )
    else:
        ccursor.execute("""
        SELECT extract(year from (day %s)) as yr, %s as data from alldata_%s WHERE station = '%s' 
         %s GROUP by yr ORDER by yr ASC
        """ % (META[cfg['plot_type']]['valid_offset'], META[cfg['plot_type']]['func'], cfg['station'][:2], cfg['station'],  
            META[cfg['plot_type']]['month_bounds']))
    ydata = []
    y50 = []
    y00 = []
    for row in ccursor:
        if row[0] < cfg['first_year'] or row[0] > cfg['last_year']:
            continue
        ydata.append( float(row[1]) )
        if row[0] > 1950 and row[0] < 1961:
            y50.append( float(row[1]) )
        if row[0] > 2000 and row[0] < 2011:
            y00.append( float(row[1]) )
            
    ydata = numpy.array( ydata )
    y50 = numpy.array( y50 )
    y00 = numpy.array( y00 )
    #print 'Content-type: text/plain\n'
    #print ydata
    #sys.exit()
    xaxis = numpy.arange(cfg['first_year'], cfg['last_year']+1)
    #ax.bar( xaxis - 0.4, ydata, fc='#336699', ec='#CCCCCC')
    ax.plot( xaxis, ydata, 'bo-')
    ax.set_title( "%s (%s - %s)\nLocation Name: %s" % (
                        META[cfg['plot_type']].get('title', 'TITLE'), cfg['first_year'], cfg['last_year'],
                        get_station_name(cfg['station'])))
    ax.set_xlabel( META[cfg['plot_type']].get('xlabel', 'XLABEL'))
    ax.set_ylabel( META[cfg['plot_type']].get('ylabel', 'YLABEL'))
    ax.set_xlim( cfg['first_year'] -1, cfg['last_year'] +1)
    miny = numpy.min(ydata)
    maxy = numpy.max(ydata)
    ax.set_ylim( miny - ((maxy-miny) / 10.), maxy + ((maxy-miny) / 10.))
    ax.grid(True)
    
    if cfg['linregress']:
        slope, intercept, r_value, p_value, std_err = stats.linregress(xaxis, ydata)
        ax.plot(xaxis, slope * xaxis + intercept, color='#CC6633')
        ax.text( cfg['first_year'], max(ydata), '$R^2$=%.2f' % (r_value ** 2,), color='#CC6633')
        #ypos = max(ydata) - (max(ydata) - min(ydata)) * 0.05
        #ax.text( cfg['first_year'], ypos, 'slope=%.2f/decade' % (slope*10,), color='#CC6633')
        #ypos = max(ydata) - (max(ydata) - min(ydata)) * 0.1
        #ax.text( cfg['first_year'], ypos, '1950 %.2f' % (numpy.average(y50),), color='#CC6633')
        #ypos = max(ydata) - (max(ydata) - min(ydata)) * 0.15
        #ax.text( cfg['first_year'], ypos, '2000 %.2f' % (numpy.average(y00),), color='#CC6633')

def dailyc_plot(ax, cfg):
    """
    Plot daily climate
    """
    COOP = iemdb.connect('coop', bypass=True)
    ccursor = COOP.cursor()
    chighs = []
    clows = []
    ccursor.execute("""
    SELECT high, low from climate51 WHERE station = 'IA0200' ORDER by valid ASC
    """)
    for row in ccursor:
        chighs.append( float(row[0]) )
        clows.append( float(row[1]) )
    chighs = numpy.array( chighs )
    clows = numpy.array( clows )

    ax.bar( numpy.arange(len(chighs)), chighs-clows, bottom=clows, width=1.0, ec='#ff0000',
            fc='#ff0000')
    
    COOP.close()

def process_cgi(form):
    """
    Handle a CGI request
    """
    cfg = {}
    cfg['station'] = form.getvalue('station')
    cfg['linregress'] = form.has_key('linregress')
    cfg['first_year'] = int(form.getvalue('first_year', 1951))
    cfg['last_year'] = int(form.getvalue('last_year', mx.DateTime.now().year - 1))
    cfg['plot_type'] = form.getvalue('plot_type', 'annual_sum_precip')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Transparent background for the plot area
    ax.patch.set_alpha(1.0)

    if cfg.get('plot_type') == 'dailyc':
        dailyc_plot(ax, cfg)
    else:
        yearly_plot(ax, cfg)

    format = form.getvalue('format', 'png')
    if format in ['eps',]:
        print "Content-Type: application/postscript\n"
    elif format in ['png',]:
        print "Content-Type: image/png\n"
    fig.savefig( sys.stdout, format=format )

if __name__ == '__main__':
    form = cgi.FieldStorage()
    if form.has_key("station"):
        process_cgi(form)