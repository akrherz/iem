"""
Check the status of our ISUSM sites being offline or online
run from RUN_40_AFTER.sh
"""
import tracker
track = tracker.Engine()
import access
import network
nt = network.Table("ISUSM")
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()
import datetime

offline = {}
icursor.execute("""SELECT station, valid from offline 
    WHERE network IN ('ISUSM')""")
for row in icursor:
    offline[ row[0] ] = row[1]

thres = datetime.datetime.now() - datetime.timedelta(hours=2)

obs = access.get_network("ISUSM", IEM)
actions = 0
for sid in obs.keys():
    ob = obs[sid]
    # back online!
    if ob.data['ts'] > thres and offline.has_key(sid):
        actions += 1
        track.checkStation(sid, {'ts': ob.data['ts'], 
                                 'sname': nt.sts[sid]['name']}, 
                           'ISUSM', 'isusm', False)
    elif ob.data['ts'] < thres and not offline.has_key(sid):
        actions += 1
        track.doAlert(sid, {'ts': ob.data['ts'], 
                                 'sname': nt.sts[sid]['name']}, 
                           'ISUSM', 'isusm', False)

if actions < 5:
    track.send()
else:
    print 'check_isusm_online had %s actions, no emails sent!' % (actions,)