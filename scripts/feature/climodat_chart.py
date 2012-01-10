import matplotlib.pyplot as plt
import numpy

def load(fp):
    data = []
    doy = []
    lines = open(fp).readlines()
    for line in lines[9:]:
        tokens = line.split()
        doy.append( tokens[0] )
        data.append( tokens[5] )
        
    return doy, data

doy, waukon = load('/mesonet/share/climodat/reports/IA8755_22.txt')
doy, ames = load('/mesonet/share/climodat/reports/IA0200_22.txt')
doy, RR = load('/mesonet/share/climodat/reports/IA7147_22.txt')
doy, fm = load('/mesonet/share/climodat/reports/IA3007_22.txt')
doy, shen = load('/mesonet/share/climodat/reports/IA7613_22.txt')

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(doy, waukon, label="Waukon (4 Nov)")
ax.plot(doy, ames, label="Ames (21 Oct)")
ax.plot(doy, RR, label="Rock Rapids (19 Oct)")
ax.plot(doy, fm, label="Fort Madison (17 Nov)")
ax.plot(doy, shen, label="Shenandoah (20 Oct)")
ax.set_yticks( numpy.arange(0,100,10))
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,306,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep 1','Oct 1','Nov 1','Dec 1') )
ax.set_title("First Fall Killing Frost Probabilities\nLow Temperature below 27$^{\circ}\mathrm{F}$, 2011 value in label")
ax.grid(True)
ax.set_ylabel("Chances of Observation before Date [%]")
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
ax.legend(loc=4,prop=prop)
ax.set_xlim(243,366)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')