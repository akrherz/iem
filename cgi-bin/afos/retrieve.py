#!/mesonet/python/bin/python
# 11 Sep 2003	Lets cleanup!

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

  #if ( os.path.isfile('/tmp/AFOS.lock') ):
  #  print 'Database is currently locked'
  #  sys.exit(0)
	

  rs = mydb.query("SELECT * from current WHERE pil = '"+pil+"' \
     ORDER by entered DESC LIMIT "+LIMIT).dictresult()
	
	
  for i in range(len(rs)):
    print rs[i]["data"]
    print "\003\001\n"
    if (len(rs) == 0):
      print "Could not Find: "+pil

Main()
