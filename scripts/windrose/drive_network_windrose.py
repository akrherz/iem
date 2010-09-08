"""
Generate a windrose for each site in the ASOS network, me thinks...
"""
from windrose.windrose import WindroseAxes
import numpy as np
import matplotlib
import matplotlib.image as image
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

import iemdb
ASOS = iemdb.connect("asos", bypass=True)
import datetime

def dosite(station):
    """
    Generate a wind rose for specified site
    """
    # Query observations
    acursor = ASOS.cursor()
    acursor.execute("""SELECT sknt, drct, valid from t2010 WHERE station = %s
        and sknt >= 0 and drct >= 0""", (station,))
    sknt = []
    drct = []
    for row in acursor:
        if len(sknt) == 0:
           minvalid = row[2]
           maxvalid = row[2]
        sknt.append( row[0] * 1.15 ) 
        drct.append( row[1] )
        if row[2] < minvalid:
            minvalid = row[2]
        if row[2] > minvalid:
            maxvalid = row[2]
    sknt = np.array( sknt )
    drct = np.array( drct )
    # Generate figure
    fig = plt.figure(figsize=(6, 7), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    ax.bar(drct, sknt, normed=True, bins=(1,2,5,7,10,15,20), opening=0.8, edgecolor='white')
    #l = ax.legend(borderaxespad=-0.1)
    #plt.setp(l.get_texts(), fontsize=8)
    #ax.set_title("Ames [KAMW] Windrose Plot")
    handles = []
    for p in ax.patches_list[1:]:
        color = p.get_facecolor()
        handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))
    l = fig.legend( handles, ('2-5','5-7','7-10','10-15','15-20','20+') , loc=3,
     ncol=6, title='Wind Speed [mph]', mode=None, columnspacing=0.9, 
     handletextpad=0.45)
    plt.setp(l.get_texts(), fontsize=10)
    # Now we put some fancy debugging info on the plot
    label = "Ames [KAMW] Windrose Plot [All Year]\nPeriod of Record: %s - %s\nNumber of Obs: %s   Calm %%: %.1f   Avg Speed: %.1f mph" % (
        minvalid.strftime("%d %b %Y"), maxvalid.strftime("%d %b %Y"), 
        len(sknt), 
        np.sum( np.where(sknt < 2., 1., 0.)) / float(len(sknt)) * 100.,
        np.average(sknt))
    plt.gcf().text(0.17,0.9, label)
    # Make a logo
    im = image.imread('../../htdocs/images/logo_small.png')
    #im[:,:,-1] = 0.8

    plt.figimage(im, 10, 625)

    plt.savefig("test.png")
    #del fig, ax, plt

if __name__ == '__main__':
    dosite("AMW")
