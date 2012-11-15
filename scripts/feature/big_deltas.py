import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

dwpfs = []
valids = []

acursor.execute("""SELECT valid, dwpf from alldata where station = 'ALO'
    and dwpf is not null and dwpf > -50 ORDER by valid ASC""")

biggest = 0

for row in acursor:
    dwpfs.append( row[1] )
    valids.append( row[0] )
    
    while (row[0] - valids[0]).days > 1:
        valids.remove(valids[0])
        dwpfs.remove(dwpfs[0])
        
    l = len(dwpfs) / 2
    if l < 2:
        continue
    delta = max(dwpfs[l:]) - min(dwpfs[:l])
    if delta > biggest and min(dwpfs) > 0:
        print 'New', delta, row[0], max(dwpfs), min(dwpfs)
        biggest = delta