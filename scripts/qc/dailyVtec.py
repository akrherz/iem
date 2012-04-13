"""
My purpose in life is to daily check the VTEC database and see if there are
any IDs that are missing.  daryl then follows up with the weather bureau
reporting anything he finds after an investigation.

$Id: $:
"""
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

tests = ['HGX.FF.7', 'GUM.MA.1', 'GUM.MA.2','MRX.SV.18', 'SGF.TO.23',
         'LMK.TO.81', 'LMK.TO.82', 'LSX.TO.11', 'IND.TO.7', 'IND.TO.8',
         'PAH.TO.52', 'PAH.TO.53','PAH.TO.54', 'PAH.TO.55', 'MRX.TO.58',
         'ILX.TO.2', 'CHS.TO.6', 'CAE.FF.1', 'CAE.TO.4', 'CAE.TO.5',
         'RNK.TO.6', 'ICT.TO.5', 'TOP.TO.5','EAX.TO.1', 'OAX.SV.22',
         'OAX.SV.21', 'OAX.SV.11', 'OAX.SV.13', 'OAX.SV.16', 'OAX.SV.17',
         'MEG.TO.32', 'HGX.TO.26', 'HGX.TO.27', 'HGX.TO.28', 'GSP.TO.12',
         'GLD.TO.1', 'GLD.TO.2', 'LBF.TO.6',
]
#for i in range(27,78):
#    tests.append('OAX.TO.%s' % (i,))
sql = "SELECT wfo, min(eventid), max(eventid), phenomena from warnings_%s \
       WHERE phenomena IN ('MA','FF','SV','TO') and significance = 'W' \
       GROUP by wfo, phenomena" % (mx.DateTime.now().year, )
rs = postgis.query(sql).dictresult()
for i in range(len(rs)):
  sEvent = int(rs[i]['min'])
  eEvent = int(rs[i]['max'])
  phenomena = rs[i]['phenomena']
  wfo = rs[i]['wfo']
  for e in range(1,sEvent):
    lookup = "%s.%s.%s" % (wfo, phenomena, e)
    if lookup not in tests:
      print "Warning Missing WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, phenomena, e)
      
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
