#!/usr/bin/env python

from pyIEM import iemdb
import mx.DateTime
i = iemdb.iemdb()
postgis = i['postgis']

def doSV():
    # Extract Polygons
    sql = "SELECT distinct * from warnings_%s WHERE wfo = 'DMX' and \
       (date(issue) = '%s' or date(expire) = '%s') \
       and gtype = 'P' and phenomena IN ('SV','TO')" % (ts.year, ts.strftime("%Y-%m-%d"), ts.strftime("%Y-%m-%d") )
    rs = postgis.query(sql).dictresult()
    cnt = len(rs)
    falseAlarms = 0
    hits = 0
    usedLSRs = [0,0]

    for i in range(len(rs)):
        issued = rs[i]['issue']
        expired = rs[i]['expire']
        geom = rs[i]['geom']
        phenomena = rs[i]['phenomena']
        # Lets go look for LSRs
        sql = "SELECT oid, * from lsrs WHERE \
               geom && SetSrid(GeometryFromText('%s'),4326) and \
               contains(SetSrid(GeometryFromText('%s'),4326), geom) \
               and valid >= '%s' and wfo = 'DMX' and \
               valid <= '%s' " % (geom, geom, issued, expired)
        rs2 = postgis.query(sql).dictresult()
        didVerify = 0
        for j in range(len(rs2)):
            rType = rs2[j]['type']
            mag   = rs2[j]['magnitude']
            oid = int(rs2[j]['oid'])
            #print rType, mag
            if (rType == "H"):
                if (float(mag) >= 0.75 and phenomena == 'SV'):
                    didVerify = 1
                    usedLSRs.append(oid)
                elif (float(mag) >= 0.75):
                    usedLSRs.append(oid)
            elif (rType == "G"):
                if (float(mag) >= 58 and phenomena == 'SV'):
                    didVertify = 1
                    usedLSRs.append(oid)
                elif (float(mag) >= 58):
                    usedLSRs.append(oid)
            elif (rType == "D"): # Damage!
                if (phenomena == 'SV'):
                    didVerify = 1
                    usedLSRs.append(oid)
                else:
                    usedLSRs.append(oid)
        if (phenomena == 'SV'):
            if (len(rs2) == 0 or didVerify == 0):
                falseAlarms += 1
            else:
                hits += 1

    # Now we find severe LSRs not covered!
    sql = "SELECT distinct * from lsrs WHERE date(valid) = '%s' and \
      oid NOT IN %s and  wfo = 'DMX' and \
      (type = 'D' or (type = 'G' and magnitude >= 58) or (type = 'H' and magnitude >= 0.75))" % (ts.strftime("%Y-%m-%d"), str(tuple(usedLSRs)),)
    #print sql
    rs3 = postgis.query(sql).dictresult()
    misses = len(rs3)

    d = {'yy': float(hits),
         'yn': float(falseAlarms),
         'ny': float(misses),
         'nn': 0.0}
    d['obs'] = d['yy'] + d['ny']
    d['warns'] = d['yy'] + d['yn']
    if (d['yy']+d['yn']+d['ny']) == 0:
        d['csi'] = -99
    else:
        d['csi'] = d['yy']/(d['yy']+d['yn']+d['ny'])
    if (d['yy']+d['yn']) == 0:
        d['far'] = -99
    else:
        d['far'] = d['ny']/(d['yy']+d['yn'])
    if (d['yy']+d['ny']) == 0:
        d['pod'] = -99
    else:
        d['pod'] = d['yy']/(d['yy']+d['ny'])
    if (d['yy']+d['ny']) == 0:
        d['bias'] = -99
    else:
        d['bias'] = (d['yy']+d['yn'])/(d['yy']+d['ny'])
    out.write("""
Severe Thunderstorm Warning:
  LSR verifying (Hail >= 0.75, Wind >= 58MPH, TSTM WND DMG)

         Observation
          Yes    No                  BIAS: %(bias).2f
        +=====+=====+                POD:  %(pod).2f
W  Yes  | %(yy)3i | %(yn)3i | %(warns)3i            FAR:  %(far).2f
A       +-----+-----+                CSI:  %(csi).2f
R  No   | %(ny)3i | N/A | 
N       +-----+-----+
          %(obs)3i   
""" % d)
# Search the DB for LSRs
# See if they meet criteria


# Print Tables

def doTO():
    # Extract Polygons
    sql = "SELECT distinct * from warnings_%s WHERE wfo = 'DMX' and \
       (date(issue) = '%s' or date(expire) = '%s') \
       and gtype = 'P' and phenomena = 'TO'" % (ts.year, ts.strftime("%Y-%m-%d"), ts.strftime("%Y-%m-%d") )
    rs = postgis.query(sql).dictresult()
    cnt = len(rs)
    falseAlarms = 0
    hits = 0
    usedLSRs = [0,0]

    for i in range(len(rs)):
        issued = rs[i]['issue']
        expired = rs[i]['expire']
        geom = rs[i]['geom']
        # Lets go look for LSRs
        sql = "SELECT oid, * from lsrs WHERE wfo = 'DMX' and \
               geom && SetSrid(GeometryFromText('%s'),4326) and \
               contains(SetSrid(GeometryFromText('%s'),4326), geom) \
               and valid >= '%s' and \
               valid <= '%s' and type = 'T'" % (geom, geom, issued, expired)
        rs2 = postgis.query(sql).dictresult()
        if (len(rs2) == 0):
            falseAlarms += 1
        else:
            hits += 1

    # Now we find severe LSRs not covered!
    sql = "SELECT distinct * from lsrs WHERE date(valid) = 'YESTERDAY' and \
      type = 'T' and wfo = 'DMX'"
    #print sql
    rs3 = postgis.query(sql).dictresult()
    misses = len(rs3)

    d = {'yy': float(hits),
         'yn': float(falseAlarms),
         'ny': float(misses),
         'nn': 0.0}
    d['obs'] = d['yy'] + d['ny']
    d['warns'] = d['yy'] + d['yn']
    if (d['yy']+d['yn']+d['ny']) == 0:
        d['csi'] = -99
    else:
        d['csi'] = d['yy']/(d['yy']+d['yn']+d['ny'])
    if (d['yy']+d['yn']) == 0:
        d['far'] = -99
    else:
        d['far'] = d['ny']/(d['yy']+d['yn'])
    if (d['yy']+d['ny']) == 0:
        d['pod'] = -99
    else:
        d['pod'] = d['yy']/(d['yy']+d['ny'])
    if (d['yy']+d['ny']) == 0:
        d['bias'] = -99
    else:
        d['bias'] = (d['yy']+d['yn'])/(d['yy']+d['ny'])

    out.write("""
Tornado Warning:

         Observation
          Yes    No                  BIAS: %(bias).2f
        +=====+=====+                POD:  %(pod).2f
W  Yes  | %(yy)3i | %(yn)3i | %(warns)3i            FAR:  %(far).2f
A       +-----+-----+                CSI:  %(csi).2f
R  No   | %(ny)3i | N/A | 
N       +-----+-----+
          %(obs)3i   
""" % d)

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
ts = mx.DateTime.DateTime(2005,7,24)

out = open('mesonet.txt', 'a')

out.write("> Unofficial NWS Polygon Warning Verification for %s\n" % (ts.strftime("%d %b %Y"), ))
out.write("*** As computed by the IEM\n")


doSV()
doTO()
out.close()
