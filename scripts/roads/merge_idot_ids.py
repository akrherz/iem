import pandas as pd
import psycopg2

pgconn = psycopg2.connect(database='postgis', host='iemdb', port=5555,
                          user='mesonet')
cursor = pgconn.cursor()

df = pd.read_excel("/tmp/cars.xlsx")

for i, row in df.iterrows():
    cursor.execute("""SELECT segid from roads_base where longname = %s
        ORDER by segid DESC""",
                   (row['LongName'], ))
    if cursor.rowcount > 1:
        print('Warning longName |%s| had %s rows' % (row['LongName'],
                                                     cursor.rowcount))
    segid = cursor.fetchone()[0]
    cursor.execute("""UPDATE roads_base SET idot_id = %s where segid = %s""",
                   (row['ID'], segid))

cursor.close()
pgconn.commit()
pgconn.close()
