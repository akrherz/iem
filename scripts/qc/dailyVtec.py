
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

tests = [
 'LMK.TO.9', 'LMK.TO.13', 'LMK.TO.14', 'ICT.TO.7', 'PAH.TO.10', 'PAH.TO.11',
 'PAH.TO.12','SGF.TO.13', 'JKL.TO.8', 'IND.TO.5', 'IND.TO.6', 'DDC.TO.2',
 'DMX.TO.2', 'FSD.TO.2', 'FSD.TO.3', 'FSD.TO.4', 'FSD.TO.5', 'FSD.TO.6',
 'OAX.TO.10', 'OAX.TO.11', 'LSX.TO.10', 'LBF.TO.3', 'UNR.TO.3', 'UNR.TO.2',
 'BOU.TO.2', 'PUB.TO.4', 'IWX.TO.7', 'GID.TO.4', 'LOT.TO.4', 'LOT.TO.3',
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
