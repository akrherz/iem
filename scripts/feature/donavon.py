#Y= 21,612 + (-2.63*X) + (0.0002808*X^2)
#where Y = 50 dBZ height in ft AGL and X = Freezing Level in ft AGL

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(111)

x = numpy.arange(5000,20000,100)
y = 21612 + (-2.63 * x) + (0.0002808 * x * x)

ax.plot(x,y)
ax.set_title("Donavon Hail Chart")
ax.set_xlabel("Freezing Level [ft AGL]")
ax.set_ylabel("50 dBZ Height [ft AGL]")
ax.grid(True)
ax.set_xlim(5000,20000)

fig.savefig('test.png')