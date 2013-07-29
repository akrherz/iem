import matplotlib.pyplot as plt
import datetime

(fig, ax) = plt.subplots(1,1)
x = []
y = []
for line in open('iowa_cape.txt'):
    tokens = line.split(",")
    fhour = float(tokens[1])
    cape = float(tokens[2])
    ts = datetime.datetime.strptime(tokens[0], '%Y-%m-%d %H:%M:%S')
    if fhour == 0 and len(x) > 0:
        ax.plot(x, y)
        x = []
        y = []
    x.append( ts + datetime.timedelta(hours=fhour))
    y.append( cape )
    
fig.savefig('test.png')

