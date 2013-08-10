"""

"""
import subprocess
import psycopg2
import datetime
import pytz
MESOSITE = psycopg2.connect(database='other', host='iemdb')
mcursor = MESOSITE.cursor()

now = datetime.datetime.now()

# Do the bubbler file
mcursor.execute("""SELECT max(valid) from ss_bubbler""")
row = mcursor.fetchone()
maxts = None if row[0] is None else datetime.datetime.strptime(
                    row[0].strftime('%m/%d/%y %H:%M:%S'), '%m/%d/%y %H:%M:%S')

for line in open('/mnt/rootdocs/Bubbler.csv'):
    tokens = line.strip().split(",")
    if len(tokens) < 2 or line[0] in ['S','G']:
        continue
    try:
        ts = datetime.datetime.strptime("%s %s" % (tokens[0], tokens[1]),
                                    '%m/%d/%Y %H:%M:%S')
    except Exception, exp:
        print exp
        print repr(line)
        continue
    if maxts and ts < maxts:
        continue
    if len(tokens) == 3:
        tokens.append( None )
    if len(tokens) == 4:
        tokens.append( None )
    mcursor.execute("""INSERT into ss_bubbler values (%s, %s, %s, %s)""" , 
                    (ts, tokens[2], tokens[3], tokens[4]))

# Do the STS_GOLD file
maxts = {}
mcursor.execute("""SELECT max(valid), site_serial from ss_logger_data
    GROUP by site_serial""")
for row in mcursor:
    maxts[ row[1] ] = datetime.datetime.strptime(row[0].strftime('%m/%d/%y %H:%M:%S'), '%m/%d/%y %H:%M:%S')

proc = subprocess.Popen("echo 'select * from logger_data' | mdb-sql -p /mnt/sts_gold/sts_gold.mdb",
                        shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

data = proc.stdout.read()
for linenum, line in enumerate(data.split("\n")):
    tokens = line.split("\t")
    if len(tokens) < 13 or linenum < 2:
        continue
    site_serial = int(tokens[1])
    ts = datetime.datetime.strptime(tokens[2], '%m/%d/%y %H:%M:%S')
    if ts > now:
        continue
    if maxts.get(site_serial) and ts < maxts.get(site_serial):
        continue
    mcursor.execute("""INSERT into ss_logger_data values (%s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s)""", tokens)
    # This won't work, sadly
    #ts = ts.replace(tzinfo=pytz.timezone("America/Chicago"))
    
mcursor.close()
MESOSITE.commit()
MESOSITE.close()