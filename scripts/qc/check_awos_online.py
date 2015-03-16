"""
Check the status of our AWOS sites being offline or online
run from RUN_10_AFTER.sh
"""
import datetime
import psycopg2
import pytz
from pyiem.tracker import TrackerEngine
from pyiem.network import Table as NetworkTable

NT = NetworkTable("AWOS")
IEM = psycopg2.connect(database='iem', host='iemdb')
PORTFOLIO = psycopg2.connect(database='portfolio', host='iemdb')


threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
threshold = threshold.replace(tzinfo=pytz.timezone("UTC"))

icursor = IEM.cursor()
icursor.execute("""SELECT id, valid from current c JOIN stations t
     ON (t.iemid = c.iemid) WHERE t.network = 'AWOS'
     """)
obs = {}
for row in icursor:
    obs[row[0]] = dict(id=row[0], valid=row[1])

tracker = TrackerEngine(IEM.cursor(), PORTFOLIO.cursor(), 10)
tracker.process_network(obs, 'iaawos', NT, threshold)
tracker.send_emails()
tac = tracker.action_count
if tac > 6:
    print 'check_awos_online.py had %s actions, did not email' % (tac,)
IEM.commit()
PORTFOLIO.commit()
