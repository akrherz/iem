import pandas as pd
# from pyiem.datatypes import temperature
import psycopg2
pgconn = psycopg2.connect(database='sustainablecorn')
cursor = pgconn.cursor()

X = {'Arlington': 'ARL', 'Marshfield': 'MAR', 'Lancaster': 'LAN'}

df = pd.read_excel("/tmp/weather11-15.xls")
print("Found %s entries, columns: %s" % (len(df.index), df.columns))
df['station'] = df['Location'].apply(lambda x: X[x])
for i, row in df.iterrows():
    # hi = temperature(row['MaxAirTemp_F'], 'F').value('C')
    # lo = temperature(row['MinAirTemp_F'], 'F').value('C')
    # print (hi+lo)/2., row['temp_C']
    cursor.execute("""INSERT into weather_data_daily(station, valid,
        high, low, precip) VALUES (%s, %s, %s, %s, %s)
        """, (row['station'], row['Date'], row['MaxAirTemp_F'],
              row['MinAirTemp_F'], row['precipitation_in']))

cursor.close()
pgconn.commit()
