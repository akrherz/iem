import matplotlib.pyplot as plt

x = []
y = []
for n in range(0,80,1):
  y.append( 0.036 * (10 ** (0.0625 * n)))
  x.append( n )

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(x,y)

fig.savefig('test.png')
