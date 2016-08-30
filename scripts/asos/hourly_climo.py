from pandas.io.sql import read_sql
import psycopg2
from pyiem.datatypes import temperature, speed, distance
from pyiem.meteorology import relh

pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

# air temperature, RH, Radiation, WS, and precipitation
df = read_sql("""SELECT valid, tmpf, dwpf, sknt, p01i,
  extract(month from valid) as month,
  extract(hour from valid + '10 minutes'::interval) as hour from alldata
  WHERE station = 'DSM' and extract(month from valid) in (10, 11)
  and extract(minute from valid) = 54
  and valid > '1986-01-01'
  """, pgconn, index_col=None)

df['relh'] = relh(temperature(df['tmpf'], 'F'),
                  temperature(df['dwpf'], 'F')).value('%')

gdf = df.groupby(by=['month', 'hour']).mean()
print gdf.at[(11, 0), 'tmpf']

pgconn = psycopg2.connect(database='isuag', host='iemdb', user='nobody')

# air temperature, RH, Radiation, WS, and precipitation
df2 = read_sql("""SELECT
  extract(month from valid) as month,
  extract(hour from valid + '10 minutes'::interval) as hour,
  c800 from hourly
  WHERE station = 'A130209' and extract(month from valid) in (10, 11)
  """, pgconn, index_col=None)

gdf2 = df2.groupby(by=['month', 'hour']).mean()

print(("MONTH,HOUR,AIRTEMP[C],"
       "RELHUMID[%],RADIATION[kC/m2],WINDSPEED[MPS],PRECIP[IN]"))
for month in (10, 11):
    for hour in range(24):
        print(("%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f"
               ) % (month, hour,
                    temperature(gdf.at[(month, hour), 'tmpf'], 'F').value('C'),
                    gdf.at[(month, hour), 'relh'],
                    gdf2.at[(month, hour), 'c800'],
                    speed(gdf.at[(month, hour), 'sknt'], 'KT').value('MPS'),
                    distance(gdf.at[(month, hour), 'p01i'], 'IN').value('MM')
                    ))
