"""Be able to merge a CSV file that IDOT provides"""
import sys
import datetime

import pandas as pd
from pyiem.util import get_dbconn

pgconn = get_dbconn('postgis')
cursor = pgconn.cursor()
xref = {}
cursor.execute("""SELECT idot_id, segid from roads_base""")
for row in cursor:
    xref[row[0]] = row[1]

ROADCOND = {
    'dry pavement': 0,
    'wet': 1,
    'partially covered with frost': 3,
    'partially covered with snow': 39,
    'partially covered with ice': 27,
    'partially covered with slush': 56,
    'partially covered with mix': 15,
    'completely covered with frost': 11,
    'completely covered with snow': 47,
    'completely covered with ice': 35,
    'completely covered with slush': 64,
    'completely covered with mixed': 23,
    'travel not advised': 51,
    'partially covered with mixed snow ice or slush': 15,
    'completely covered with mixed snow ice or slush': 23,
    'icy bridges': 27,
    'seasonal': 0,
    'Seasonal': 0,
    'seasonal roadway conditions': 0,
    'impassable': 86,
            }

df = pd.read_csv(sys.argv[1])
for i, row in df.iterrows():
    segid = xref[int(row['SEGMENT_ID'])]
    condcode = ROADCOND[row['HL_PAVEMENT_CONDITION']]
    ts = datetime.datetime.strptime(str(row['CARS_MSG_UPDATE_DATE']),
                                    '%Y%m%d%H%M%S')
    cursor.execute("""INSERT into roads_2015_2016_log(segid, valid, cond_code,
    raw) VALUES (%s, %s, %s, %s)""", (segid, ts, condcode,
                                      row['HL_PAVEMENT_CONDITION']))

cursor.close()
pgconn.commit()
