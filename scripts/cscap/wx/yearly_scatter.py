import psycopg2
import matplotlib.pyplot as plt
import numpy as np

pgconn = psycopg2.connect(database='coop')
cursor = pgconn.cursor()

def run(station):
    cursor.execute("""SELECT model, scenario, extract(year from day) as yr,
    sum(precip) from hayhoe_daily WHERE station = %s and precip > 0
    and precip is not null
    GROUP by model, scenario, yr ORDER by yr""", (station,))
    data = {}
    for row in cursor:
        key = "%s_%s" % (row[0], row[1])
        if not data.has_key(key):
            data[key] = {'years': [], 'total': []}
        data[key]['years'].append(row[2])
        data[key]['total'].append(row[3])
    
    markers = ['o', 'v', '1', '2', '3', '4', '8', '+', 'x','d']
    colors = ['r', 'g', 'b', 'k', 'r', 'g', 'b', 'k', 'r', 'g']
    (fig, ax) = plt.subplots(1,1)
    for i, key in enumerate(data):
        yr = np.array(data[key]['years'])
        tot = np.ma.fix_invalid(data[key]['total'])
        avg = np.ma.average(tot)
        ax.scatter(yr, tot, marker=markers[i], label="%s %.2f" % (key, avg),
                   s=40, color=colors[i])

        # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
                 box.width, box.height * 0.8])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=3, scatterpoints=1, fontsize=10)
    ax.grid(True)
    ax.set_xlim(1958, 2100)
    ax.set_ylabel("Annual Precipitation [inch]")
    ax.set_title("Ames, Iowa ISUAG CMIP3 Hayhoe Dataset\nYearly Precipitation Totals (avg shown in legend)")
    fig.savefig('test.png')
    

run('IA0200')