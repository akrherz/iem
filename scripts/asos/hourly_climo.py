from pandas.io.sql import read_sql
import psycopg2
from pyiem.datatypes import temperature, speed, distance
from pyiem.meteorology import relh

pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

# air temperature, RH, Radiation, WS, and precipitation
df = read_sql("""SELECT valid, tmpf, dwpf, sknt, p01i,
  extract(month from valid) as month,
  extract(hour from valid + '10 minutes'::interval) as hour,
  extract(day from valid + '10 minutes'::interval) as day from alldata
  WHERE station = 'DSM' and extract(month from valid) in (10, 11)
  and extract(minute from valid) = 54
  and valid > '1986-01-01'
  """, pgconn, index_col=None)

df['relh'] = relh(temperature(df['tmpf'], 'F'),
                  temperature(df['dwpf'], 'F')).value('%')

gdf = df.groupby(by=['month', 'day', 'hour']).mean()

pgconn = psycopg2.connect(database='isuag', host='iemdb', user='nobody')

# air temperature, RH, Radiation, WS, and precipitation
df2 = read_sql("""SELECT
  extract(month from valid) as month,
  extract(hour from valid + '10 minutes'::interval) as hour,
  extract(day from valid + '10 minutes'::interval) as day,
  c800 from hourly
  WHERE station = 'A130209' and extract(month from valid) in (10, 11)
  """, pgconn, index_col=None)

gdf2 = df2.groupby(by=['month', 'day', 'hour']).mean()

print(("MONTH,DAY,HOUR,AIRTEMP[C],"
       "RELHUMID[%],RADIATION[kC/m2],WINDSPEED[MPS],PRECIP[MM]"))
for month in (10, 11):
    for day in range(1, 32):
        if day == 31 and month == 11:
            continue
        for hour in range(24):
            print(("%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f"
                   ) % (month, day, hour,
                        temperature(gdf.at[(month, day, hour),
                                           'tmpf'], 'F').value('C'),
                        gdf.at[(month, day, hour), 'relh'],
                        gdf2.at[(month, day, hour), 'c800'],
                        speed(gdf.at[(month, day, hour), 'sknt'],
                              'KT').value('MPS'),
                        distance(gdf.at[(month, day, hour), 'p01i'],
                                 'IN').value('MM')
                        ))
