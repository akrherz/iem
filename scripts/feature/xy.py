
from matplotlib import pyplot as plt
import numpy
from scipy import stats

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
asos = i['asos']

d1 = [  37.0640873908997,
 39.1891688108444,
 35.8661621809006,
 32.9181373119354,
 41.4145052433014,
 49.3994265794754,
 53.4239292144775,
  50.935286283493,
 42.8313612937927,
 35.1625859737396,
 32.9993277788162,
 40.4708713293076]

d2 = [ 40.1868969202042,
 32.5547784566879,
 40.6256705522537,
 41.8095827102661,
 40.6708717346191,
 38.4331166744232,
 51.4878809452057,
 55.7360887527466,
  42.904344201088,
 41.9715225696564,
  31.827238202095,
 35.8833223581314]

fig = plt.figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(numpy.arange(12), d1, 0.35, color='b')
rects2 = ax.bar(numpy.arange(12)+0.35, d2, 0.35, color='r')
ax.legend( (rects1[0], rects2[0]), ('1973-1989', '1990-2010') )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( numpy.arange(12)+0.35)
ax.set_title("Des Moines Precip Contribution\n12-8 AM versus rest of day")
ax.set_ylabel('Percentage [%]')

a = 9. / 24. * 100.0
ax.plot([0,12], [a,a], color='#000000')

fig.savefig("test.png")
