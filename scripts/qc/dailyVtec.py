
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

tests = [
 'LSX.TO.11', 'CAE.TO.2', 'GSP.TO.5', 'PAH.SV.10', 'JKL.TO.4', 'LWX.TO.3',
 'RNK.TO.2', 'IND.TO.7', 'IND.TO.8', 'LMK.TO.12', 'LMK.TO.13', 'LMK.TO.14',
 'PAH.TO.17', 'PAH.TO.18', 'PAH.TO.19', 'PAH.TO.20', 'PAH.TO.21',
 'MEG.TO.20', 'ICT.TO.6', 'OAX.TO.8', 'DMX.TO.16', 'FSD.TO.2', 'SGF.TO.10',
 'LSX.TO.16', 'ILX.TO.2', 'RLX.TO.2', 'RLX.TO.3', 'MPX.TO.5', 'MPX.TO.6',
 'MPX.TO.7', 'FSD.TO.16', 'FSD.TO.17', 'FSD.TO.18', 'ARX.TO.9', 'ARX.TO.10',
 'ARX.TO.11', 'GRB.TO.17', 'GRB.TO.18', 'GRB.TO.19', 'DLH.TO.2', 'DLH.TO.3',
 'MKX.TO.2', 'MKX.TO.3', 'MEG.SV.449', 'MEG.SV.450', 'MEG.SV.451','MEG.SV.452',
 'MEG.SV.453','MEG.SV.454','MEG.SV.455','MEG.SV.456','MEG.SV.457','MEG.SV.458',
 'MEG.SV.459','MEG.SV.460','MEG.SV.461','CAE.SV.113', 'LUB.SV.56', 'MLB.SV.72',
 'LBF.SV.186','MQT.MA.52','PIH.SV.29','PIH.SV.30',
]
for i in range(2,69):
    tests.append('VEF.SV.%s' % (i,))
for i in range(21,30):
    tests.append('OAX.FF.%s' % (i,))
for i in range(228,248):
    tests.append('OAX.SV.%s' % (i,))
    
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
