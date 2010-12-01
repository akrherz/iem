import iemdb, network

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

st = network.Table('IACLIMATE')

for id in st.sts.keys():
    ccursor.execute("""
    SELECT year, month, sum(precip) from alldata where
    stationid = %s GROUP by year, month ORDER by year, month
    """, (id.lower(),))
    l = 0
    for row in ccursor:
        if l == 0 and row[2] == 0:
            print 'Deleting', stationid, row[0], row[1]
            ccursor2.execute("""UPDATE alldata SET precip = null
            where stationid = %s and month = %s and year = %s""",
            (id.lower(), row[1], row[0]))
        l = row[2]
        
ccursor2.close()
COOP.commit()