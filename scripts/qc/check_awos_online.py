"""
Check the status of our AWOS sites being offline or online
run from RUN_10_AFTER.sh
"""
import tracker
track = tracker.Engine()
import access
import network
nt = network.Table("AWOS")
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
import mx.DateTime

offline = {}
icursor.execute("""SELECT station, valid from offline 
    WHERE network IN ('AWOS')""")
for row in icursor:
    offline[ row[0] ] = row[1]

thres = mx.DateTime.now() - mx.DateTime.RelativeDateTime(hours=1)

obs = access.get_network("AWOS", IEM)
actions = 0
for sid in obs.keys():
    ob = obs[sid]
    # back online!
    if ob.data['ts'] > thres and offline.has_key(sid):
        actions += 1
        track.checkStation(sid, {'ts': ob.data['ts'], 
                                 'sname': nt.sts[sid]['name']}, 
                           'AWOS', 'iaawos', False)
    elif ob.data['ts'] < thres and not offline.has_key(sid):
        actions += 1
        track.doAlert(sid, {'ts': ob.data['ts'], 
                                 'sname': nt.sts[sid]['name']}, 
                           'AWOS', 'iaawos', False)

print actions
if actions < 10:
    track.send()