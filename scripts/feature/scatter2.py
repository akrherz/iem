import numpy
from matplotlib import pyplot as plt

data = """40.324,9.756
43.724,-35.000
44.250,24.996
41.250,33.703
42.900,8.382
41.000,10.233
38.519,13.731
41.584,31.576
35.000,23.004
45.800,14.956
31.951,35.189
37.100,34.421
42.995,25.194
38.336,23.553
39.735,19.936
38.400,16.854
60.897,8.980
36.962,19.388
37.950,27.454
36.166,23.345
56.696,-3.162
41.950,28.680
46.800,28.432
40.400,18.794
40.319,31.257
41.000,13.726
48.062,26.662
43.092,26.443
38.940,25.883
44.052,-13.771
60.550,7.398
38.665,21.713
53.200,11.714
40.393,25.988
45.468,30.386
42.417,25.754
40.250,24.242
43.745,7.211
36.000,25.811
43.627,10.704
44.015,-5.509
57.450,10.021
60.035,10.131
42.750,30.810
40.550,32.034
38.550,18.507
45.672,24.599
37.850,18.467
44.735,-35.000
49.514,10.131
41.400,36.608
44.162,-35.000
40.261,26.144
42.050,29.844
45.770,20.714
38.943,31.985
51.119,9.328"""
tmpf = []
dbz = []
for line in data.split("\n"):
  tokens = line.split(',')
  tmpf.append( float(tokens[0]))
  dbz.append( float(tokens[1]))


import numpy as np
import matplotlib.pyplot as plt


fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(dbz, tmpf)
ax.set_xlabel("Average NEXRAD Reflectivity [dBZ]")
ax.set_ylabel("Average Air Temperature [F]")
ax.set_title("Iowa Airport Sites between 12-4 PM on 2 Nov 2011")
ax.set_xlim(-30,45)
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")
#plt.savefig("test.png")
