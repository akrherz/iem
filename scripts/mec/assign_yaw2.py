"""
Update the database with the new yaw values!
"""
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import warnings
from pyiem.util import get_dbconn
warnings.simplefilter("ignore", RuntimeWarning)

PGCONN = get_dbconn("mec",  user="mesonet")
cursor = PGCONN.cursor()
PGCONN2 = get_dbconn("asos", user="mesonet")
acursor = PGCONN2.cursor()

def process(xedges, yedges, counts):
    # For each AWOS Wind bin, lets find the index of max frequency
    x = []
    correction = []
    for i, bin in enumerate(xedges[:-1]):
        x.append(xedges[i])
        if not np.isnan( np.nanmax(counts[i,:]) ): 
            diff = yedges[ np.nanargmax(counts[i,:]) ] - xedges[i]
            if diff > 180:
                diff -= 360.0
            if diff < -180:
                diff += 360.0
        else:
            diff = 0
        correction.append( 0 - diff )
        
    return x, correction

def compute_correction(unitnumber, turbineid):
    """ Compute what the bias is for this turbine """
    cursor2 = PGCONN.cursor()
    
    # Go find interesting cases!
    acursor.execute("""
      SELECT valid, drct from alldata where station = 'SLB'
      and extract(hour from valid) between 8 and 16 and sknt > 10
      and valid between '2008-08-01' and '2008-09-15'
      """)
    asos = []
    turbine = []
    valid = []
    for row in acursor:
        cursor2.execute("""SELECT yaw from sampled_data_"""+unitnumber+""" 
        where valid = %s and yaw is not null""", 
                       (row[0],))
        if cursor2.rowcount == 0:
            continue
        row2 = cursor2.fetchone()
        asos.append( float(row[1]) )
        turbine.append( float(row2[0]) )
        valid.append(row[0])
    if len(valid) < 2:
        print 'missing'
        return
        
    turbine = np.array(turbine)
        
    (fig, ax) = plt.subplots(4,1, figsize=(7,10))
    (counts, xedges, yedges, img) = ax[0].hist2d(asos, turbine, bins=36, cmin=5)
    ax[0].set_ylabel("Turbine %s" % (turbineid,))

    x, correction = process(xedges, yedges, counts)

    basis = 0
    cor_stddev = np.std(correction)
    if cor_stddev > 30: #arb threshold
        # lets shift the data 180 and try again!
        basis = 180.
        turbine2 = turbine + 180.
        turbine2 = np.where(turbine2>360, turbine2-360., turbine2)
        
        (counts, xedges, yedges) = np.histogram2d(asos, turbine2, bins=36)
                
        x, correction = process(xedges, yedges, counts)
        cor_stddev2 = np.std(correction)
        print '[180adj old: %.1f new: %.1f]' % (cor_stddev, cor_stddev2),
        
    fig.colorbar(img, ax=ax[0])
    ax[0].set_xlabel("Storm Lake AWOS Wind Direction")
    ax[0].plot([0,360], [0,360], lw=2, zorder=2, color='k')
    ax[0].set_title("AWOS Wind Direction vs Turbine Yaw frequency comparison")
    ax[0].grid(True)
        
    ax[1].bar(x, correction, ec='b', fc='b', width=(xedges[1]-xedges[0]))
    bias = np.average(correction) + basis
    ax[1].axhline( bias, lw=2, c='k' )
    ax[1].set_ylim(min(correction)-5, max(correction)+5)
    ax[1].grid(True)
    ax[1].set_xlim(0,360)
    ax[1].set_xlabel("AWOS Wind Direction")
    ax[1].set_ylabel("Bias Correction (basis=%s)" % (basis,))
    
    turbine2 = turbine + bias
    turbine2 = np.where(turbine2 >= 360, turbine2 - 360, turbine2)
    turbine2 = np.where(turbine2 < 0, turbine2 + 360, turbine2)
    
    (counts, xedges, yedges, img) = ax[2].hist2d(asos, turbine2, bins=36, cmin=1)
    fig.colorbar(img, ax=ax[2])
    ax[2].set_xlabel("Storm Lake AWOS Wind Direction")
    ax[2].set_ylabel("Turbine %s Corrected (%.1f)" % (turbineid, bias))
    ax[2].plot([0,360], [0,360], lw=2, zorder=2, color='k')
    ax[2].set_title("AWOS vs Turbine %s Corrected" % (turbineid,))
    ax[2].grid(True)
    
    t = np.array(turbine)
    a = np.array(asos)
    diff = t - a
    diff = np.where(diff > 180, a - t, diff)
    diff = np.where(diff < -180, diff + 360., diff)
    
    
    ax[3].grid(True)
    ax[3].scatter(valid, diff)
    ax[3].set_ylabel("Turbine-ASOS [deg]")
    ax[3].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    
    fig.tight_layout()
    
    fig.savefig('yaw_correction_plots/yaw3_correction_%s.png' % (turbineid,))
    plt.close()
    return bias

def update_database(unitnumber, turbineid, correction):
    """ Apply this correction """
    cursor2 = PGCONN.cursor()
    cursor2.execute("""UPDATE sampled_data_"""+unitnumber+""" 
        SET yaw3 = yaw + %s where valid between '2008-08-01' and '2008-09-01'""", 
                       (correction,))
    cursor2.execute("""UPDATE sampled_data_"""+unitnumber+"""
        SET yaw3 = yaw3 - 360. WHERE yaw3 > 360 and
        valid between '2008-08-01' and '2008-09-01'""")

    cursor2.execute("""UPDATE sampled_data_"""+unitnumber+"""
        SET yaw3 = yaw3 + 360. WHERE yaw3 < 0 and
        valid between '2008-08-01' and '2008-09-01'""")
    
    cursor2.close()
    PGCONN.commit()

def main():
    """ Do stuff """
    cursor.execute("""select unitnumber, id from turbines""")
    for row in cursor:
        print 'ID: %s' % (row[1],),
        correction = compute_correction(row[0], row[1])
        if correction is None:
            continue
        print '... correction: %.1f' % (correction,)
        if abs(correction) > 5:
            update_database(row[0], row[1], correction)
        else:
            update_database(row[0], row[1], 0)


if __name__ == '__main__':
    # Go Main
    main()