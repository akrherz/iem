'''
 Util script to reprocess some data for Magda
'''

import psycopg2

pgconn = psycopg2.connect(database='mesosite')
cursor = pgconn.cursor()

cursor.execute("""SELECT year, month, sum(precip), avg(high), avg(low)
 from kbs GROUP by year, month""")

data = {}

for row in cursor:
    data["%s%s" % (row[0], row[1])] = {'prec': row[2], 'tmax': row[3],
                                       'tmin': row[4]}
o = open('kbs_century.txt', 'w')

for year in range(1951,2013):
    for col in ['prec', 'tmin', 'tmax']:
        o.write("%s  %s" % (col, year))
        for i in range(1,13):
            o.write("%7.2f" % (data["%s%s" % (year, i)][col],))
        o.write("\n")
        
        
o.close()