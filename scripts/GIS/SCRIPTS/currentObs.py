#!/usr/bin/python
#	currentObs.csh
# Script that dumps current observations into a DB
# Daryl Herzmann 4 Sept 2001
# 14 Jan 2002:	Don't use meteor
#  6 Jun 2002:	Code audit, insert into postgis db
#		Also do RWIS information
# 18 Nov 2002:	Ahhh, how did this ever work?
#
#####################################################

import pg


mydb = pg.connect('iowa')
postgis = pg.connect('postgis')
mydb.query("SET TIME ZONE 'GMT'")

def insert(rs):
  thisValid = "No Surface Data"
  for i in range(len( rs )):
    thisStation = rs[i]["station"]
    thisTemp = rs[i]["tmpf"]
    thisDwpf = rs[i]["dwpf"]
    thisDrct = rs[i]["drct"]
    thisSknt = rs[i]["sknt"]
    thisValid = rs[i]["valid"]
    postgis.query("UPDATE current SET tmpf = "+str(thisTemp)+", \
     dwpf = "+ str(thisDwpf) +", drct = "+ str(thisDrct) +", \
     sknt = "+ str(thisSknt) +" WHERE station = '"+ thisStation +"' ")
  return thisValid

rs = mydb.query("SELECT station, valid, \
  tmpf, dwpf, drct, sknt from azos WHERE \
  valid = to_char(CURRENT_TIMESTAMP, \
  'YYYY-mm-dd HH24:00')::timestamp ").dictresult()

postgis.query("UPDATE current SET tmpf = -9999, dwpf = -9999, sknt = -9999, \
  drct = -9999 WHERE network = 'Z'")
thisValid = insert(rs)

rs = mydb.query("SELECT station, valid, \
  tmpf, dwpf, drct, sknt from rwis WHERE \
  valid = to_char(CURRENT_TIMESTAMP, \
  'YYYY-mm-dd HH24:00')::timestamp ").dictresult()

postgis.query("UPDATE current SET tmpf = -9999, dwpf = -9999, sknt = -9999, \
  drct = -9999 WHERE network = 'R'")
thisValid = insert(rs)

print thisValid
