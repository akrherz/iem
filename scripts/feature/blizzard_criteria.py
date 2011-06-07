# Lets run some diagnostics on blizzard criterion

import pylab
import iemdb, network
import numpy
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
st = network.Table( ('IA_ASOS', 'AWOS') )

bestvsby = {}
bestsknt = {}
bs_vsby = []
bs_sknt = []
bv_vsby = []
bv_sknt = []

abestvsby = {}
abestsknt = {}
abs_vsby = []
abs_sknt = []
abv_vsby = []
abv_sknt = []
hits = {}
ahits = {}

for id in st.sts.keys():
    bestvsby[id] = {'sknt': 0, 'vsby': 100}
    bestsknt[id] = {'sknt': 0, 'vsby': 100}
    abestvsby[id] = {'sknt': 0, 'vsby': 100}
    abestsknt[id] = {'sknt': 0, 'vsby': 100}
    
    icursor.execute("""
    SELECT valid, vsby, sknt from current_log WHERE
    station = %s and valid > '2011-02-01 12:00' and
    sknt >= 0 and vsby >= 0 ORDER by valid ASC
    """, (id,))
    valid = []
    sknt = []
    vsby = []
    for row in icursor:
        valid.append( row[0] )
        sknt.append( row[2] )
        vsby.append( row[1] )
    # Now, we process...
    obs  = len(valid)
    if obs < 10:
        continue
    for i in range(obs):
        j = i
        while j < obs and (valid[j] - valid[i]).seconds < (3*3600):
            j += 1
        avg_sknt = numpy.average( numpy.array(sknt[i:j]) )
        min_sknt = min( sknt[i:j] )
        avg_vsby = numpy.average( numpy.array(vsby[i:j]) )
        max_vsby = max( vsby[i:j] )
        if avg_sknt >= 30 and avg_vsby <= 0.25:
            ahits[id] = True
        if min_sknt >= 30 and max_vsby <= 0.25:
            hits[id] = True
            #print 'Hit %s %s %s %s %s' % (id, valid[i], valid[j-1],
            #                min_sknt, max_vsby)
        if min_sknt > bestsknt[id]['sknt']:
            bestsknt[id]['sknt'] = min_sknt
            bestsknt[id]['vsby'] = max_vsby
        if max_vsby < bestvsby[id]['vsby']:
            bestvsby[id]['sknt'] = min_sknt
            bestvsby[id]['vsby'] = max_vsby
            
        if avg_sknt > abestsknt[id]['sknt']:
            abestsknt[id]['sknt'] = avg_sknt
            abestsknt[id]['vsby'] = avg_vsby
        if avg_vsby < abestvsby[id]['vsby']:
            abestvsby[id]['sknt'] = avg_sknt
            abestvsby[id]['vsby'] = avg_vsby


    bv_sknt.append( bestvsby[id]['sknt'] )
    bv_vsby.append( bestvsby[id]['vsby'] )
    bs_sknt.append( bestsknt[id]['sknt'] )
    bs_vsby.append( bestsknt[id]['vsby'] )
    abv_sknt.append( abestvsby[id]['sknt'] )
    abv_vsby.append( abestvsby[id]['vsby'] )
    abs_sknt.append( abestsknt[id]['sknt'] )
    abs_vsby.append( abestsknt[id]['vsby'] )

def log_10_product(x, pos):
    """The two args are the value and tick position.
    Label ticks with the product of the exponentiation"""
    return '%1i' % (x)


print 'A hits', len(ahits.keys())
print 'Hits', len( hits.keys() )
print hits.keys()

import matplotlib.pyplot as plt

fig = plt.figure()
fig.text(.5,.97, "Iowa ASOS/AWOS 11-12 Dec 2010 Blizzard Criteria", ha='center')
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

ax1.set_ylim(0,45)
ax1.set_ylabel("Minimum 3HR Wind Speed [mph]")
ax2.set_ylabel("Average 3HR Wind Speed [mph]")
ax2.set_ylim(0,45)
ax1.set_xlim(1e-1,1.2e1)
ax2.set_xlim(1e-1,1.2e1)
ax1.set_xlabel("Maximum 3HR Visibility [miles]")
ax2.set_xlabel("Average 3HR Visibility [miles]")

ax1.plot([1e-1,1.2e1], [30*1.15,30*1.15], 'g--')
ax1.plot([0.25,0.25], [0,45], 'g--')
ax2.plot([1e-1,1.2e1], [30*1.15,30*1.15], 'g--')
ax2.plot([0.25,0.25], [0,45], 'g--')

ax1.scatter(bs_vsby, numpy.array(bs_sknt) * 1.15, marker='+', color='r', label='Best Wind')
ax1.scatter(bv_vsby, numpy.array(bv_sknt) * 1.15, marker='o', facecolor='w', edgecolor='b', label="Best Vis")
ax1.set_xscale('log')
ax1.legend()

ax2.scatter(abs_vsby, numpy.array(abs_sknt) * 1.15, marker='+', color='r', label='Best Wind')
ax2.scatter(abv_vsby, numpy.array(abv_sknt) * 1.15, marker='o', facecolor='w', edgecolor='b',label='Best Vis')
ax2.set_xscale('log')
ax2.legend()

formatter = pylab.FuncFormatter(log_10_product)
ax1.xaxis.set_major_formatter(formatter)
ax2.xaxis.set_major_formatter(formatter)

ax1.set_title(" \nMax/Min Method: %s/%s Sites Hit" % (
                            len(hits), len(bs_vsby)))
ax2.set_title(" \nAverage Method: %s/%s Sites Hit" % (
                            len(ahits), len(abs_vsby)))

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
