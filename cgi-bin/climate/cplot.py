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
from matplotlib import pyplot as plt
import iemdb
import numpy
import mx.DateTime
import network
from scipy import stats

META = {
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
    else:
        ccursor.execute("""
        SELECT extract(year from (day %s)) as yr, %s as data from alldata_%s WHERE station = '%s' 
         %s GROUP by yr ORDER by yr ASC
        """ % (META[cfg['plot_type']]['valid_offset'], META[cfg['plot_type']]['func'], cfg['station'][:2], cfg['station'],  
            META[cfg['plot_type']]['month_bounds']))
    ydata = []
    for row in ccursor:
        if row[0] < cfg['first_year'] or row[0] > cfg['last_year']:
            continue
        ydata.append( float(row[1]) )
    ydata = numpy.array( ydata )
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