import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
from pyiem.network import Table as NetworkTable
import sys
sys.path.insert(0, "/mesonet/www/apps/iemwebsite/scripts/lib")
from windrose.windrose import WindroseAxes
from matplotlib.patches import Rectangle


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW', label='Select Station:'),
    ]
    return d

def plotter( fdict ):
    """ Go """
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    

    cursor.execute("""
     SELECT valid, drct, sknt from alldata where station = %s and 
     presentwx ~* 'TS' and sknt > 0 and drct >= 0 and drct <= 360
    """, (station,))
    sped = []
    drct = [] 
    for i, row in enumerate(cursor):
        if i == 0:
            minvalid = row[0]
            maxvalid = row[0]
        if row[0] < minvalid: minvalid = row[0]
        if row[0] > maxvalid: maxvalid = row[0]
        sped.append( row[2] * 1.15)
        drct.append( row[1] )

        
    fig = plt.figure(figsize=(6, 7), facecolor='w', edgecolor='w')
    rect = [0.1, 0.09, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    ax.bar(drct, sped, normed=True, bins=[0,2,5,7,10,15,20], opening=0.8, 
           edgecolor='white', nsector=18)
    handles = []
    for p in ax.patches_list:
        color = p.get_facecolor()
        handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))
    l = fig.legend( handles, ('2-5','5-7','7-10','10-15','15-20','20+') , loc=3,
     ncol=6, title='Wind Speed [%s]' % ('mph',), 
     mode=None, columnspacing=0.9, handletextpad=0.45)
    plt.setp(l.get_texts(), fontsize=10)
    
    plt.gcf().text(0.5,0.99, ("%s-%s %s Wind Rose\n%s\nWhen METAR observation "
                              +"includes thunderstorm (TS)") % (minvalid.year,
                            maxvalid.year, station, nt.sts[station]['name']), 
                   fontsize=16, ha='center', va='top')
    plt.gcf().text(0.01, 0.1, "Generated: 8 September 2014" ,
                       verticalalignment="bottom")
    plt.gcf().text(0.95, 0.1, "n=%s" % (len(drct),) ,
                       verticalalignment="bottom", ha='right')


    return fig
