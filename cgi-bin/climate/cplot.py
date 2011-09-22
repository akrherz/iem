#!/mesonet/python/bin/python
"""
Gonna try to make something that can plot most anything under the moon for the COOP 
data, watch me fail

-  seasonal temperatures, ex: summer daily max. temperature
-  seasonal percipitation, ex: summer annual precip.
-  growing degree days
-  heating degree days


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
  }, 
 'annual_avg_temp': {
    'title': 'Annual Average Temperature',
    'ylabel': 'Temperature [F]',
    'xlabel': 'Year',   
    'func': 'avg((high+low)/2.)',       
  },  
 'frost_free': {
    'title': 'Frost Free Days',
    'ylabel': 'Days',
    'xlabel': 'Year',   
    'func': '',       
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
        SELECT year, %s as data from alldata_%s WHERE station = '%s' and
        year >= %s and year <= %s GROUP by year ORDER by year ASC
        """ % (META[cfg['plot_type']]['func'], cfg['station'][:2], cfg['station'], cfg['first_year'], 
           cfg['last_year']))
    ydata = []
    for row in ccursor:
        ydata.append( float(row[1]) )
    ydata = numpy.array( ydata )
    #print 'Content-type: text/plain\n'
    #print ydata
    #sys.exit()
    xaxis = numpy.arange(cfg['first_year'], cfg['last_year']+1)
    ax.bar( xaxis - 0.4, ydata, fc='#336699', ec='#CCCCCC')
    ax.set_title( "%s (%s - %s)\nLocation Name: %s" % (
                        META[cfg['plot_type']].get('title', 'TITLE'), cfg['first_year'], cfg['last_year'],
                        get_station_name(cfg['station'])))
    ax.set_xlabel( META[cfg['plot_type']].get('xlabel', 'XLABEL'))
    ax.set_ylabel( META[cfg['plot_type']].get('ylabel', 'YLABEL'))
    ax.set_xlim( cfg['first_year'] -1, cfg['last_year'] +1)
    ax.set_ylim( numpy.min(ydata) - 3, numpy.max(ydata) + 3)
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