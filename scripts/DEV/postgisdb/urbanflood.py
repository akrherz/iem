'''
 Dump stats on Urban Flood Advisory
'''
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = POSTGIS.cursor()

cursor.execute("""
 SELECT foo.ugc, count, name, state from 
 (SELECT ugc, count(*) from warnings_2012 WHERE
 significance = 'Y' and phenomena = 'FA' and report ~* 'URBAN AND SMALL STREAM'
 GROUP by ugc) as foo, nws_ugc n WHERE n.ugc = foo.ugc ORDER by ugc ASC""")

for row in cursor:
    print '%s,%s,%s,%s' % (row[0], row[1], row[2], row[3])