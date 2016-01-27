"""Look into which autoplots have not been used in a while"""
import psycopg2
import re
import pandas as pd

QRE = re.compile("q=([0-9]+)")

pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT valid, appurl from feature WHERE appurl is not null
    and appurl != ''
    """)
q = {}
for row in cursor:
    appurl = row[1]
    valid = row[0]
    if appurl.find("/plotting/auto/") != 0:
        continue
    tokens = QRE.findall(appurl)
    if len(tokens) == 0:
        print("appurl: %s valid: %s failed RE" % (appurl, valid))
        continue
    appid = int(tokens[0])
    res = q.setdefault(appid, valid)
    if res < valid:
        q[appid] = valid

df = pd.DataFrame.from_dict(q, orient='index')
df.columns = ['valid']
maxval = df.index.max()
for i in range(1, maxval):
    if i not in q:
        print("No entries for: %4i" % (i, ))
df.sort_values(by='valid', inplace=True)
print df.head()
