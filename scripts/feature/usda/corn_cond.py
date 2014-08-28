"""
 We get the data from: http://www.nass.usda.gov/
"""
import numpy as np
from PIL import Image
import datetime

def get(state):
    condition = np.ma.zeros((2015-1986,52), 'f')
    juliandate = np.ma.zeros((2015-1986,52), 'f')
    
    for line in open('/home/akrherz/Downloads/20266C73-6B39-3DDC-A680-7393899883D1.csv').readlines()[1:]:
        tokens = line.replace('"','').split(",")
        year = int(tokens[1])
        if tokens[5] != state:
            continue
        week = int(tokens[2][6:8])
        date = datetime.datetime.strptime(tokens[3], '%Y-%m-%d')
        condcode = tokens[16].strip()
        condval = tokens[19].replace('"', '').strip()
        if condval == "":
            continue
        #print year, week, date, condcode, condval
        if condcode in ['MEASURED IN PCT POOR', 
                        'MEASURED IN PCT VERY POOR']:
            condition[year-1986,week-1] += float(condval)
        juliandate[year-1986,week-1] = float(date.strftime("%j"))
            
    juliandate.mask = np.where(juliandate == 0, True, False)
    if state == 'ILLINOIS':
        print np.max(condition, 1)
    return condition, juliandate

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

states = ['IOWA', 'ILLINOIS', 'MINNESOTA', 'WISCONSIN', 'MISSOURI', 'INDIANA']
fig, ax = plt.subplots(3,2, sharex=True, sharey=True)

i = 0
for row in range(3):
    for col in range(2):
        colors = ['black',  'green', 'blue', 'red', 'brown']
        condition, juliandate = get(states[i])
    
        for yr in range(1986,2015):
            if yr in [1993,2014,2012,1988,2005]:
                ax[row,col].plot( juliandate[yr-1986,:], condition[yr-1986,:], 
                                  c=colors.pop(), 
                         label='%s' % (yr,), lw=3, zorder=2)
            else:
                ax[row,col].plot( juliandate[yr-1986,:], condition[yr-1986,:], c='tan',
                                  zorder=1)
        if row == 1 and col == 1:
            ax[row,col].legend(ncol=5, loc=(-0.95,1.02), prop=prop)
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

fig.text(0.5, .91, 'USDA Weekly Corn Crop Condition Report (1986-2014)\nPercentage of State in Poor & Very Poor Condition\n(2014 thru 24 August)', ha='center')

logo = Image.open('../../../htdocs/images/logo_small_white.png')
ax3 = plt.axes([0.12,0.91,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
ax3.imshow(logo)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')