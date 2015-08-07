import psycopg2

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()
pgconn2 = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = pgconn2.cursor()

cursor.execute("""select f.valid, r.dwpc from raob_profile_2015 r 
    JOIN raob_flights f ON (f.fid = r.fid) WHERE f.station = 'KOAX' 
    and extract(hour from f.valid) = 7 
    and valid > '2015-06-01' and r.pressure = 925 ORDER by valid""")

valid = []
diff = []
dwpc = []
for row in cursor:
  acursor.execute("""SELECT station, avg(dwpf) from t2015 where
  station in ('AMW', 'DSM') and extract(hour from valid) = 15
  and date(valid) = %s GROUP by station""", (row[0].strftime("%Y-%m-%d"),))
  data = {}
  for row2 in acursor:
    data[row2[0]] = row2[1]

  valid.append(row[0])
  diff.append(data['AMW'] - data['DSM'])
  dwpc.append(row[1])

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2, 1)

ax[0].set_title("3 PM Ames + Dew Moines Dew Point Comparison")
ax[0].scatter(dwpc, diff)
ax[0].set_ylabel("AMW - DSM DewPoint [F]")
ax[0].set_xlabel("Omaha 12 UTC 925 hPa Dew Point [C]")
ax[1].bar(valid, diff)
ax[1].set_ylabel("AMW - DSM DewPoint [F]")

fig.savefig('test.png')
