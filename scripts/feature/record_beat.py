import iemdb

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select sday, high, day from alldata_ia where station = 'IA2203' ORDER by day ASC
""")
records = {}
running = 0
for row in ccursor:
    old = records.get(row[0], -99)
    if row[1] >= old:
        records[row[0]] = row[1]
        running += 1
    else:
        running = 0
    if running > 1:
        print row, running
    #if (row[1] - old) > 9:
    #    print row, old