import copy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

values = [1,2,3,4,5,6,7,8,9,10,90,91,92,93,94,95,96,97,98,99]

print 'MO,MIN,1,2,3,4,5,6,7,8,9,10,90,91,92,93,94,95,96,97,98,99,MAX'

for month in range(1,13):
    ccursor.execute("""
    SELECT high, max(r) from (
select high, percent_rank() over (order by high) as r  from 
 alldata_ia where high is not null and month = %s
 and station not in ('IA0000', 'IAC001', 'IAC002','IAC003','IAC004','IAC005','IAC006','IAC007','IAC008','IAC009')
 and station in (select distinct station from alldata_ia where year = 1931
 and precip > 0)
 ) as foo GROUP by high ORDER by high ASC
""", (month,))
    #v = copy.deepcopy(values)
    xs = []
    ys = []
    for row in ccursor:
        xs.append( row[1] * 100.0 )
        ys.append( row[0] )
    print '%s,%s,' % (month,ys[0]),
    for v in values:
        t = -99
        mindist = 1000
        for x,y in zip(xs, ys):
            dist = abs(x - v)
            if dist < mindist:
                #print 'Match', x, v, y
                mindist = dist
                t = y
        print '%s,' % (t,),

    print "%s" % (ys[-1],)
