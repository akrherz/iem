import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""SELECT valid, precip from alldata_1minute WHERE station = 'DSM' 
 and precip > 0 ORDER by valid ASC""")

output = open('DSM_1min.txt', 'w')
output.write("Date,Time,Precip[in]\n")
for row in acursor:
    output.write('%s,%s,%s\n' %(row[0].strftime("%Y/%m/%d"), row[0].strftime("%I:%M %p"), row[1]))
    
output.close()