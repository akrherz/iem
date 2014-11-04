""" Take a file of flight info and add METAR obs to it! """
import datetime
import psycopg2.extras
import pytz
pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def get_data(sid, valid):
    """ Go get data for this time! """
    if sid[0] == 'K':
        sid = sid[1:]
    
    cursor.execute("""SELECT valid at time zone 'UTC' as utctime, * 
    from alldata WHERE valid BETWEEN %s and %s and station = %s""",
    (valid - datetime.timedelta(hours=1), 
     valid + datetime.timedelta(hours=1), sid))
    
    mindelta = datetime.timedelta(hours=2)
    ret = {}
    for row in cursor:
        utc = row['utctime'].replace(tzinfo=pytz.timezone("UTC"))
        if utc > valid:
            diff = utc - valid
        else:
            diff = valid - utc
        if diff < mindelta:
            ret = row.copy()
            mindelta = diff

    return ret

def timefmt(val):
    """ Nice formatter """
    if val is None:
        return "NULL"
    return val.strftime("%Y-%m-%d %H:%M:%S.000")

o = open('flight.csv', 'w')

for linenum, line in enumerate(
            open('/tmp/FlightActivtyJan2011.csv').read().split("\r")):
    if linenum < 2:
        continue
    if linenum % 1000:
        print 'Processed %s lines...' % (linenum,)
    tokens = line.split(",")
    deptime = datetime.datetime.strptime(tokens[3][:19], '%Y-%m-%d %H:%M:%S')
    deptime = deptime.replace(tzinfo=pytz.timezone("UTC"))
    arrtime = datetime.datetime.strptime(tokens[6][:19], '%Y-%m-%d %H:%M:%S')
    arrtime = arrtime.replace(tzinfo=pytz.timezone("UTC"))
    depicao = tokens[4]
    arricao = tokens[5]
    
    arrdata = get_data(arricao, arrtime)
    depdata = get_data(depicao, deptime)
    
    o.write("%s,%s,%s,%s,%s,%s,%s\n" % (line, depdata.get('station', 'NULL'),
                                timefmt(depdata.get('utctime')),
                                depdata.get('metar', 'NULL').replace("\n", " "),
                                arrdata.get('station', 'NULL'),
                                timefmt(arrdata.get('utctime')),
                                arrdata.get('metar', 'NULL').replace("\n", " ")
                                ))
    
o.close()
