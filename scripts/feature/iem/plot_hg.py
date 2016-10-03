import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

pgconn = psycopg2.connect(database='hads', host='iemdb-hads', user='nobody')
cursor = pgconn.cursor()


def get_station(station):
    cursor.execute("""
        SELECT distinct valid, value from raw2015_07 where
        station = %s and valid > '2015-07-06' and key = 'HGIRGZ'
        ORDER by valid ASC
    """, (station, ))
    rows = []
    for row in cursor:
        rows.append(dict(valid=row[0], value=row[1]))

    return pd.DataFrame(rows)


(fig, ax) = plt.subplots(1, 1)

for station in ['MIWI4', 'TMAI4', 'TAMI4', 'BPLI4', 'MROI4']:
    df = get_station(station)
    ax.plot(df['valid'], df['value'], label=station)

ax.legend(loc='best')
fig.savefig('test.png')
