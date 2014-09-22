import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

x = []
# Result file from assign_yaw2.py
for line in open('corrections.txt'):
    x.append( float(line.split()[-1]))
    

(fig, ax) = plt.subplots(1,1)
ax.set_ylabel("Turbine Count")
ax.set_title("Histogram of Applied Yaw Corrections")
ax.set_xlabel("Yaw Correction $^\circ$")
ax.hist(x, bins=36)
ax.set_xlim(-360,360)
ax.set_xticks(range(-360,361,60))
ax.grid(True)

fig.savefig('test.png')