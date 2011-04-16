
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

tests = [
 'LSX.TO.11', 'CAE.TO.2', 'GSP.TO.5', 'PAH.SV.10', 'JKL.TO.4', 'LWX.TO.3',
 'RNK.TO.2', 'IND.TO.7', 'IND.TO.8', 'LMK.TO.12', 'LMK.TO.13', 'LMK.TO.14',
 'PAH.TO.17', 'PAH.TO.18', 'PAH.TO.19', 'PAH.TO.20', 'PAH.TO.21',
 'MEG.TO.20', 'ICT.TO.6', 'OAX.TO.8', 'DMX.TO.16', 'FSD.TO.2', 'SGF.TO.10',
 'LSX.TO.16', 'ILX.TO.2'
]

sql = "SELECT wfo, min(eventid), max(eventid), phenomena from warnings_%s \
       WHERE phenomena IN ('MA','FF','SV','TO') and significance = 'W' \
       GROUP by wfo, phenomena" % (mx.DateTime.now().year, )
rs = postgis.query(sql).dictresult()
for i in range(len(rs)):
  sEvent = int(rs[i]['min'])
  eEvent = int(rs[i]['max'])
  phenomena = rs[i]['phenomena']
  wfo = rs[i]['wfo']

  for eventid in range(sEvent, eEvent):
    sql = "SELECT gtype, count(*) as c from warnings_%s WHERE wfo = '%s' \
           and phenomena = '%s' and eventid = '%s' and significance = 'W' \
           GROUP by gtype" % (mx.DateTime.now().year, wfo,\
           phenomena, eventid)
    rs2 = postgis.query(sql).dictresult()
    polyCount = 0
    cntyCount = 0
    for q in range(len(rs2)):
      if (rs2[q]['gtype'] == "P"): polyCount = int(rs2[q]['c'])
      if (rs2[q]['gtype'] == "C"): cntyCount = int(rs2[q]['c'])

    if (cntyCount == 0 and polyCount == 0):
      lookup = "%s.%s.%s" % (wfo, phenomena, eventid)
      if lookup not in tests:
        print "Warning Missing WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, phenomena, eventid)
    elif (polyCount == 0):
      print "SBW Missing     WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, phenomena, eventid)
    elif (cntyCount == 0):
      print "County Missing  WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, phenomena, eventid)
    elif (polyCount > 1):
      print "Duplicate SBW   WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, phenomena, eventid)
      sql = "DELETE from warnings_%s WHERE oid IN (\
         SELECT max(oid) as m from warnings_%s WHERE wfo = '%s' \
         and phenomena = '%s' and eventid = '%s' and significance = 'W' \
         and gtype = 'P')" % (mx.DateTime.now().year, mx.DateTime.now().year,\
          wfo, phenomena, eventid)
      postgis.query(sql) 
      sql = "DELETE from warnings_%s WHERE oid IN (\
              select m from (\
select ugc,  max(oid) as m, count(oid) as c from warnings_%s WHERE wfo = '%s' \
and phenomena = '%s' and eventid = '%s' and significance = 'W' \
and gtype = 'C' GROUP by ugc) as foo WHERE c > 1)" % (mx.DateTime.now().year, mx.DateTime.now().year,\
          wfo, phenomena, eventid)
      postgis.query(sql)
