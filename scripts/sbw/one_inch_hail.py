# Look for wind information in warnings

import re
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

# Query for warnings
rs = postgis.query("""SELECT issue, windtag, report, wfo, eventid, 
    issue, expire, astext(geom) as txt 
    from sbw WHERE wfo = 'DMX' and status = 'NEW' and 
    significance = 'W' and phenomena = 'SV'""").dictresult()

# Loop over them, doing verification
for i in range(len(rs)):
    r = rs[i]['report'].replace("\n", "")
    tokens = re.findall("([0-9]{1,3})\s+MPH", r)
    if len(tokens) == 0 and rs[i]['windtag'] is None:
        continue
    print "%s,%s,%s,%s" % (rs[i]['issue'], rs[i]['eventid'], 
        rs[i]['windtag'] or tokens[-1],
        ",".join(tokens))
    continue
    sql = "SELECT * from lsrs_2007 WHERE wfo = '%s' and \
      valid >= '%s' and valid < '%s' and \
      ((type = 'H' and magnitude >= 0.75) \
       or (type = 'G' and magnitude >= 58) or type = 'D') and\
      geom && SetSrid(GeometryFromText('%s'),4326) and \
      contains(SetSrid(GeometryFromText('%s'),4326), geom)" % (rs[i]['wfo'],
      rs[i]['issue'], rs[i]['expire'], rs[i]['txt'], rs[i]['txt'])
    rs2 = postgis.query(sql).dictresult()
    verif = {}
    for k in range(len(rs2)):
        typ = rs2[k]['type']
        mag = rs2[k]['magnitude']
        if typ == 'H' and mag >= 1:
            verif['L'] = 1
        elif typ == 'H' and mag < 1:
            verif['S'] = 1
        elif typ == 'D':
            verif['D'] = 1
        elif typ == 'G':
            verif['G'] = 1

    # Now we think
    if len(rs2) == 0:
        unverified += 1
    else:
        verifsz[sz] += 1
    if not verif.has_key('D') and not verif.has_key('G') and not verif.has_key('L') and verif.has_key('S'):
        small_only += 1
    if verif.has_key('L'):
        large_verif += 1
    if verif.has_key('S'):
        small_verif += 1
    if verif.has_key('D'):
        damage_verif += 1
    if verif.has_key('G'):
        wind_verif += 1
        
print """
Total Warnings     :  %s  [ %s unverified ]
Verified Warnings  :  %s
 - Small Hail Only :  %s
 + Large Hail      :  %s
 + Small Hail      :  %s
 + Tstorm Damage   :  %s
 + Wind Damage     :  %s
""" % (warnings, unverified, warnings - unverified, small_only, large_verif, small_verif, damage_verif, wind_verif)

print mentioned
print verifsz
