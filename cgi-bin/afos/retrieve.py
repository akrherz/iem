#!/mesonet/python/bin/python

import pg, cgi, string, os, sys

def Main():
  print 'Content-type: text/plain \n\n'
  try:
    mydb = pg.connect('afos', 'mtarchive.geol.iastate.edu', user='nobody')
  except:
    print 'Error Connecting to Database, please try again!'
    sys.exit(0)

  myForm = cgi.FormContent()
  pil = "%6s" %  (string.upper( myForm["pil"][0] ) + "      ",)
  LIMIT = str( myForm["limit"][0] )

  if ( len(pil) < 3):
    print 'Invalid PIL, try again'
    sys.exit(0)


  rs = mydb.query("SELECT * from current WHERE pil = '"+pil+"' \
     ORDER by entered DESC LIMIT "+LIMIT).dictresult()
	
	
  for i in range(len(rs)):
    print rs[i]["data"]
    print "\003\001\n"

  if (len(rs) == 0 and pil[:3] != "MTR"):
    print "Could not Find: "+pil

  if (len(rs) == 0 and pil[:3] == "MTR"):
    print "%s doesn't exist in AFOS database, looking in IEM's archive\n" % (pil,)
    access = pg.connect('iem', '10.10.10.20', user='nobody')
    sql = "SELECT raw from current WHERE station = '%s'" % (pil[3:],)
    print sql
    rs = access.query( sql ).dictresult()
    if (len(rs) == 1):
      print rs[0]['raw']
    
    if (LIMIT > 1):
      sql = "SELECT raw from current_log WHERE station = '%s' ORDER by valid DESC LIMIT %s" % (pil[3:], LIMIT)
      print sql
      rs = access.query( sql ).dictresult()
      for i in range(len(rs)):
        print rs[i]['raw']
        print "\003\001\n"
         

Main()
