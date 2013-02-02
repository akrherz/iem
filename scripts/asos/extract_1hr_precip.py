import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""SELECT valid, p01m from alldata WHERE station = 'DSM' 
 and p01m > 0 ORDER by valid ASC""")

output = open('DSM_1hr.txt', 'w')
output.write("Date,Time,Precip[in]\n")
for row in acursor:
    output.write('%s,%s,%.2f\n' %(row[0].strftime("%Y/%m/%d"), row[0].strftime("%I:%M %p"), row[1] / 25.4))
    
output.close()
