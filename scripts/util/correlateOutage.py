#!/mesonet/python/bin/python

from pyIEM import stationTable, iemdb
import mx.DateTime, re
i = iemdb.iemdb()
portfolio = i['portfolio']

network1 = stationTable.stationTable("/mesonet/TABLES/awos.stns")
network2 = stationTable.stationTable("/mesonet/TABLES/RWIS.stns")

sts = mx.DateTime.DateTime(2004,1,1)
ets = mx.DateTime.DateTime(2005,1,1)

data = {}

for net in ['iaawos','iarwis']:
  data[net] = {}
  # Get tickets for this network
  tickets = portfolio.query("SELECT * from tt_base WHERE portfolio = '%s' \
    and subject = 'Site Offline' and author = 'mesonet' and s_mid != 'ADU' \
    ORDER by id ASC" % (net, ) ).dictresult()


  for i in range(len(tickets)):
    id = str(tickets[i]["id"])
    sid = tickets[i]["s_mid"]
    e = tickets[i]['entered'][:16]
    in_ts = mx.DateTime.strptime( e, '%Y-%m-%d %H:%M')
    log = portfolio.query("SELECT * from tt_log WHERE tt_id = "+ id +" \
      and comments ~* 'Site Back Online at:' ").dictresult()
    if len(log) == 1:
      comments = log[0]["comments"]
      tokens = re.split(" ", comments)
      backOnline = tokens[-2] +" "+ tokens[-1]
      try:
        out_ts = mx.DateTime.strptime( backOnline , '%Y-%m-%d %H:%M:00.00')
      except:
        continue
      now = in_ts + mx.DateTime.RelativeDateTime(hours=+1,minute=0)
      #while (now < out_ts):
      if (not data[net].has_key(sid)):
        data[net][sid] = {}
      data[net][sid][now] = 1
    #    now += mx.DateTime.RelativeDateTime(hours=+1)

awoses = data['iaawos'].keys()
rwises = data['iarwis'].keys()

for awos in awoses:
  hits = {}
  for s in awoses:
    hits[s] = 0

  for ts in data['iaawos'][awos]:
    for sid in awoses:
      if (data['iaawos'][sid].has_key(ts) and sid != awos):
        hits[sid] += 1

  maxVal = 0
  maxSID = 0
  for id in hits:
    if (maxVal < hits[id]):
      maxVal = hits[id]
      maxSID = id
  print "%s:  %s %s" % (awos, maxSID, maxVal)
  
