#!/mesonet/python/bin/python

import pg, cgi, string, os, sys

def Main():
  print 'Content-type: text/plain; charset=""'
  print
  print
  try:
    mydb = pg.connect('afos', 'iem20', user='nobody')
  except:
    print 'Error Connecting to Database, please try again!'
    sys.exit(0)

  myForm = cgi.FormContent()
  if (myForm.has_key("pil")):
    pil0 = string.upper( myForm["pil"][0] )
  else:
    print "Bad, you must specify $pil"
    return
  if (myForm.has_key("limit")):
    LIMIT = str( myForm["limit"][0] )
  else:
    LIMIT = "1"

  pils = pil0.split(",")
  myPils = []
  for pil in pils:
    if ( len(pil) < 3):
      print 'Invalid PIL, try again'
      sys.exit(0)
    if (pil[:3] == "WAR"):
      for q in ['FFS','AWW','TOR','SVR','FFW','SVS','LSR']:
        pils.append('%s%s' % (q, pil[3:]) )
      continue
    myPils.append("%6s" % (pil + "      ",) )

  pilAR = "("
  for pil in myPils:
    pilAR += "'%s'," % (pil,)
  pilAR = pilAR[:-1] +")"
  
  sql = "SELECT * from current WHERE pil IN "+ pilAR +" \
   ORDER by entered DESC LIMIT "+LIMIT

  #mydb.query("set enable_seqscan=no")
  print sql
  rs = mydb.query(sql).dictresult()
	
	
  for i in range(len(rs)):
    print (rs[i]["data"]).replace("\003", "").replace("\001", "")
    print "\003\001\n"

  if (len(rs) == 0 and myPils[0][:3] != "MTR"):
    print "Could not Find: "+pil

  if (len(rs) == 0 and myPils[0][:3] == "MTR"):
    #print "%s doesn't exist in AFOS database, looking in IEM's archive\n" % (pil,)
    access = pg.connect('iem', 'iemdb', user='nobody')
    sql = "SELECT raw from current_log WHERE raw != '' and station = '%s' ORDER by valid DESC LIMIT %s" % (myPils[0][3:].strip(), LIMIT)
    rs = access.query( sql ).dictresult()
    for i in range(len(rs)):
      print rs[i]['raw']
      print "\003\001\n"
         

Main()
