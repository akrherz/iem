import psycopg2

pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
for v in range(1, 6):
    for n in ['moisture', 'temp', 'ec']:
        if v > 1 and n == 'ec':
            continue
        cursor = pgconn.cursor()
        cursor.execute("""UPDATE decagon_data SET
        d%s%s_flag = 'M', d%s%s = null WHERE d%s%s = -999
        """ % (v, n, v, n, v, n))
        print "%s rows with -999 set to null for d%s%s" % (cursor.rowcount, v,
                                                           n)
        cursor.close()
        pgconn.commit()
pgconn.close()
