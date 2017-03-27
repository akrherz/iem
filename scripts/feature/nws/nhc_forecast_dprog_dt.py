from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.font_manager
import psycopg2

fig = plt.figure(num=None, figsize=(9.3, 7.00))
ax = plt.axes([0.15, 0.1, 0.75, 0.75], axisbg=(0.4471, 0.6235, 0.8117))

m = Basemap(projection='merc',
            urcrnrlat=55.7, llcrnrlat=19.08, urcrnrlon=-61.5, llcrnrlon=-97,
            lon_0=-68.7, lat_0=29, lat_1=23, lat_2=35,
            resolution='l', ax=ax, fix_aspect=False)
m.fillcontinents(color='0.7', zorder=0)
m.drawcountries(zorder=1)
m.drawstates(zorder=1)
m.drawcoastlines(zorder=1)

AFOS = psycopg2.connect(database='afos', host='iemdb', user='nobody')
acursor = AFOS.cursor()

acursor.execute("""SELECT data, entered from products_2005_0712
    WHERE pil = 'TCDAT2'
 and entered > '2005-08-15' and entered < '2005-09-10'
 ORDER by entered ASC""")

verify_x = []
verify_y = []
verify_speed = []


def get_color(speed):
    if speed < 40:
        return '#FFFFFF', 1
    if speed < 75:
        return '#0000FF', 2
    if speed < 96:
        return '#00FF00', 3
    if speed < 111:
        return '#FF0000', 4
    if speed < 130:
        return '#0000FF', 5
    if speed < 157:
        return '#00FFFF', 6


for row in acursor:
    print row[1]
    track_x = []
    track_y = []
    colors = []
    tokens = row[0].split("FORECAST POSITIONS AND MAX WINDS")
    for line in tokens[1].split("\n"):
        parts = line.replace('HR VT', 'HR').strip().split()
        if len(parts) < 5:
            continue
        print parts
        lat = float(parts[2].replace("N", ""))
        lon = 0 - float(parts[3].replace("W", ""))
        x, y = m(lon, lat)
        speed = float(parts[4])
        # ax.text(x,y, parts[6])
        if parts[0] == "INITIAL":
            verify_x.append(lon)
            verify_y.append(lat)
            verify_speed.append(speed)
        track_x.append(lon)
        track_y.append(lat)
        c, z = get_color(speed)
        if parts[0] != "INITIAL":
            if track_x[-2] - track_x[-1] > 5:
                continue
            print track_x, track_y
            x, y = m(track_x[-2:], track_y[-2:])
            ax.plot(x, y, color=c, linestyle='-', linewidth=2, zorder=z)

for i in range(1, len(verify_x)):
    x, y = m(verify_x[i-1:i+1], verify_y[i-1:i+1])
    c, z = get_color(verify_speed[i])
    ax.plot(x, y, color='#FFFFFF', linewidth=4, linestyle="-", zorder=7)
    ax.plot(x, y, color=c, linewidth=2, linestyle="-", zorder=8)

l2 = Line2D([], [], linewidth=3, color=get_color(74)[0])
l3 = Line2D([], [], linewidth=3, color=get_color(95)[0])
l4 = Line2D([], [], linewidth=3, color=get_color(110)[0])

prop = matplotlib.font_manager.FontProperties(size=10)

ax.set_title(("National Hurricane Center\n"
              "Forecast Positions & Max Wind (TCD Product) for Katrina (2005)"
              ), size=14)
ax.set_xlabel(("Forecasts made between 4 PM 23 Aug 2005\n"
               "and 10 AM 30 Aug 2005, outlined is observation"), size=14)
ax.legend([l2, l3, l4], ["Tropical Storm", "Category 1", "Category 2"],
          prop=prop, loc=2)

fig.savefig('test.png')
