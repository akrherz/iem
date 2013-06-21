#Y= 21,612 + (-2.63*X) + (0.0002808*X^2)
#where Y = 50 dBZ height in ft AGL and X = Freezing Level in ft AGL

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(111)

x = numpy.arange(5000,20000,100)
y = 14669 + (-0.5713329 * x) + (0.0001632 * x * x)
ax.plot(x,y, label='1 inch')

x = numpy.arange(5000,20000,100)
y = 10809 + (-0.1286213 * x) + (0.00014275 * x * x)
ax.plot(x,y, label='0.75 inch')


ax.set_title("Donavon Hail Chart")
ax.set_xlabel("Freezing Level [ft AGL]")
ax.set_ylabel("50 dBZ Height [ft AGL]")
ax.grid(True)
ax.set_xlim(5000,20000)
ax.legend(loc=2)

fig.savefig('test.png')