import numpy
import numpy.ma
import mx.DateTime.ISO
import Image

def get(state):
    condition = numpy.ma.zeros((2013-1986,52), 'f')
    juliandate = numpy.ma.zeros((2013-1986,52), 'f')
    
    for line in open('corn_condition.csv').readlines()[1:]:
        tokens = line.replace('"','').split(",")
        year = int(tokens[1])
        if tokens[5] != state:
            continue
        week = int(tokens[2][6:8])
        date = mx.DateTime.strptime(tokens[3], '%Y-%m-%d')
        condcode = tokens[15].strip()
        condval = tokens[19].replace('"', '').strip()
        if condval == "":
            continue
        #print year, week, date, condcode, condval, float(date.strftime("%j"))
        if condcode in ['POOR', 'VERY POOR']:
            condition[year-1986,week-1] += float(condval)
        juliandate[year-1986,week-1] = float(date.strftime("%j"))
            
    juliandate.mask = numpy.where(juliandate == 0, True, False)
    if state == 'ILLINOIS':
        print numpy.max(condition, 1)
    return condition, juliandate

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

states = ['IOWA', 'ILLINOIS', 'MINNESOTA', 'WISCONSIN', 'MISSOURI', 'INDIANA']
fig, ax = plt.subplots(3,2, sharex=True, sharey=True)

i = 0
for row in range(3):
    for col in range(2):
        colors = ['black',  'green', 'blue','red']
        condition, juliandate = get(states[i])
    
        for yr in range(1986,2013):
            if yr in [1993,2012,1988,2005]:
                ax[row,col].plot( juliandate[yr-1986,:], condition[yr-1986,:], c=colors.pop(), 
                         label='%s' % (yr,), lw=3, zorder=2)
            else:
                ax[row,col].plot( juliandate[yr-1986,:], condition[yr-1986,:], c='tan',
                                  zorder=1)
        if row == 1 and col == 1:
            ax[row,col].legend(ncol=4, loc=(-0.75,1.02), prop=prop)
        ax[row, col].set_xticks( (121,152, 182,213,244,274,305,335,365) )
        ax[row, col].set_xticklabels( ('May', 'Jun', 'Jul','Aug','Sep','Oct','Nov','Dec') )
        ax[row, col].set_xlim(120,310)
        ax[row, col].grid(True)
        ax[row, col].set_ylim(0,100)
        if col == 0:
            ax[row, col].set_ylabel("Coverage [%]")
        ax[row, col].set_title(" ")
        ax[row, col].text(126, 85, states[i].capitalize(), size=16)
        i += 1

#ax[0,0].set_title("USDA Weekly Crop Progress Report (1979-2012)\nIowa Corn Planting Progress (6 years highlighted)")

fig.text(0.5, .91, 'USDA Weekly Corn Crop Condition Report (1986-2012)\nPercentage of State in Poor & Very Poor Condition\n(2012 thru 12 August)', ha='center')

logo = Image.open('../../htdocs/images/logo_small_white.png')
ax3 = plt.axes([0.10,0.91,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
ax3.imshow(logo, origin='lower')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')