import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8,8))

ax = fig.add_subplot(111)

ax.plot( [0,100], [0,100] )
ax.set_xlabel("Temperature after the sun goes down $^{\circ}F$")
ax.set_ylabel("Temperature when the sun goes up $^{\circ}F$")
ax.set_title("My Fancy Plot!!!")

fig.savefig('test.png', dpi=(40))
