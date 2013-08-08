#!/usr/bin/env python

import cgi
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import memcache
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mpcolors

def run(station, gddbase):
    ''' Run! '''
    import numpy as np
    import psycopg2
    import datetime
    import network
    nt = network.Table("%sCLIMATE" % (station[:2].upper(),))
    today = datetime.datetime.now()
    byear = nt.sts[station]['archive_begin'].year
    eyear = today.year + 1
    DBCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = DBCONN.cursor()
    table = "alldata_%s" % (station[:2],)
    cursor.execute("""SELECT year, extract(doy from day), 
        gddxx(50, 86, high,low), low 
         from """+table+""" where station = %s and year > %s """, (station,
                                    byear))

    gdd = np.zeros( (eyear-byear, 366), 'f')
    freeze = np.zeros( (eyear-byear), 'f')
    freeze[:] = 400.0

    for row in cursor:
        gdd[ row[0] - byear, row[1] - 1] = row[2]
        if row[1] > 180 and row[3] < 32 and row[1] < freeze[row[0] - byear]:
            freeze[row[0]- byear] = row[1]
            
    for i in range(len(freeze)):
        gdd[i, freeze[i]:] = 0.0

    idx = int(datetime.datetime.now().strftime("%j")) - 1
    apr1 = int(datetime.datetime(2000,4,1).strftime("%j")) - 1
    jun30 = int(datetime.datetime(2000,6,30).strftime("%j")) - 1
    sep1 = int(datetime.datetime(2000,9,1).strftime("%j")) - 1
    oct31 = int(datetime.datetime(2000,10,31).strftime("%j")) - 1

    # Replace all years with the last year's data
    scenario_gdd = gdd *1
    scenario_gdd[:-1,:idx] = gdd[-1,:idx]
    
    # store our probs
    probs = np.zeros( (oct31-sep1, jun30-apr1 ), 'f')
    scenario_probs = np.zeros( (oct31-sep1, jun30-apr1 ), 'f')
    
    for x in range(apr1,jun30):
        for y in range(sep1,oct31):
            sums = np.where(np.sum( gdd[:-1,x:y], 1) >= gddbase, 1, 0)
            probs[y-sep1,x-apr1] = sum(sums) / float(len(sums)) * 100.0
            sums = np.where(np.sum( scenario_gdd[:-1,x:y], 1) >= gddbase, 1, 0)
            scenario_probs[y-sep1,x-apr1] = sum(sums) / float(len(sums)) * 100.0
    
    probs = np.where(probs < 0.1, -1, probs)
    scenario_probs = np.where(scenario_probs < 0.1, -1, scenario_probs)
    
    
    (fig, ax) = plt.subplots(1,2, sharey=True)
    
    cmap = cm.get_cmap('jet')
    cmap.set_under('white')
    norm = mpcolors.BoundaryNorm(np.arange(0,101,5), cmap.N)
    
    res = ax[0].imshow(np.flipud(probs), aspect='auto',extent=[apr1,jun30,sep1,oct31],
                       interpolation='nearest', vmin=0, vmax=100, cmap=cmap,
                       norm=norm)
    ax[0].grid(True)
    ax[0].set_title("Overall Frequencies")
    ax[0].set_xticks( (91,106,121,136,152,167) )
    ax[0].set_ylabel("Growing Season End Date")
    ax[0].set_xlabel("Growing Season Begin Date")
    ax[0].set_xticklabels( ('Apr 1', '15', 'May 1','15','Jun 1','15') )
    ax[0].set_yticks( (244,251,258, 265, 274,281, 288, 295, 305) )
    ax[0].set_yticklabels( ('Sep 1', 'Sep 8', 'Sep 15', 'Sep 22', 'Oct 1','Oct 8', 'Oct 15', 'Oct 22', 'Nov') )
    
    res = ax[1].imshow(np.flipud(scenario_probs), aspect='auto', extent=[apr1,jun30,sep1,oct31],
                       interpolation='nearest', vmin=0, vmax=100, cmap=cmap,
                       norm=norm)
    ax[1].grid(True)
    ax[1].set_title("%s Scenario to %s" % (today.year, today.strftime("%-d %B")))
    ax[1].set_xticks( (91,106,121,136,152,167) )
    ax[1].set_xticklabels( ('Apr 1', '15', 'May 1','15','Jun 1','15') )
    ax[1].set_xlabel("Growing Season Begin Date")
    
    fig.subplots_adjust(bottom=0.20,top=0.85)
    cbar_ax = fig.add_axes([0.05, 0.05, 0.85, 0.05])
    fig.colorbar(res, cax=cbar_ax, orientation='horizontal')
    
    fig.text(0.5, 0.90, "%s-%s %s GDDs\nFrequency [%%] of reaching %.0f GDDs prior to first freeze" % (byear,
                                                                                eyear-1,
                    nt.sts[station]['name'], gddbase,), fontsize=16,
             ha='center')
    
    
def postprocess():
    import Image
    import cStringIO
    ram = cStringIO.StringIO()
    plt.savefig(ram, format='png')
    ram.seek(0)
    im = Image.open(ram)
    im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    ram = cStringIO.StringIO()
    im2.save( ram, format='png')
    ram.seek(0)
    return ram.read()

def main():
    """ Lets do this! """
    form = cgi.FieldStorage()
    station = form.getvalue('station', 'IA0200')[:6]
    gddbase = int(form.getvalue('gddbase', 2600))
    
    mckey = "/cgi-bin/climate/gdd_probs.py|%s|%s" % (station, 
                                                    gddbase)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    sys.stdout.write("Content-type: image/png\n\n")
    if not res:
        run(station, gddbase)
        res = postprocess()
        mc.set(mckey, res)
    sys.stdout.write( res )

if __name__ == '__main__':
    main()