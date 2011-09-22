import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

ccursor.execute("""
SELECT valid, max_high, max_high_yr from climate where station = 'ia2203' ORDER by valid
""")
for row in ccursor:
    acursor.execute("""
    SELECT valid, tmpf from t%s WHERE station = 'DSM' and 
    valid BETWEEN '%s-%s 00:00' and '%s-%s 23:59' ORDER by tmpf DESC LIMIT 1
    """ % (row[2], row[2], row[0].strftime("%m-%d"), row[2], row[0].strftime("%m-%d")))
    row2 = acursor.fetchone()
    if row2 is None:
        print row
        continue
    if row2[0].hour < 13:
        print row[0], row[1], row[2], row2[0], row2[1]