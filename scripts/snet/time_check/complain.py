"""
 Complain about things, this is what I do best
"""
import network
nt = network.Table("KCCI")
import psycopg2
portfolio = psycopg2.connect('dbname=portfolio host=iemdb user=nobody')
pcursor = portfolio.cursor()


lines = open("times.txt", 'r').readlines()

print '%-5s %-30.30s %s' % ('ID', 'Location Name', 'Time Difference [secs]')
emails = {}
bad = 0
for line in lines:
    t = line.split("|")
    sid = t[0]
    if not nt.sts.has_key(sid):
        continue
    sname = t[1]
    dur = float(t[2])
    if dur < 1000 and dur > -1000:
        continue
    print "%s %-30.30s %s" % (sid, sname, dur)
    sql = """SELECT email from iem_site_contacts WHERE portfolio = 'kccisnet' 
         and s_mid = %s"""
    args =  (sid, )
    pcursor.execute(sql, args)
    for row in pcursor:
        emails[ row[0] ] = 1
    bad += 1

print
print '%s sites with clocks out of bounds' % (bad,)
print 
for k in emails.keys():
    print "%s," % (k,),

