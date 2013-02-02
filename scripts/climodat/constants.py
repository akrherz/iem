
import pg
import mx.DateTime

_THISYEAR = 2013
_ENDYEAR = 2014
#_ENDYEAR = 1951

_ARCHIVEENDTS = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
_ENDTS = mx.DateTime.DateTime(2014,1,1)
#_YEARS = 58
#_YRCNT = [0,58,58,58,57,57,57,57,57,57,57,57,57]
mydb = pg.connect('coop', 'iemdb',user='nobody')
import iemdb
mesosite = iemdb.connect('mesosite', bypass=True)
mcursor = mesosite.cursor()
mcursor.execute("""SELECT propvalue from properties 
    where propname = 'iaclimate.end'""")
row = mcursor.fetchone()
_QCENDTS = mx.DateTime.strptime(row[0], '%Y-%m-%d')
mcursor.close()

longterm = ['IA1635','IA4063','IA3509','IA3473','IA4389','IA5769','IA1319',
'IA7147','IA2171','IA1533','IA5952','IA2110','IA6243','IA5131','IA3290',
'IA8266','IA7979','IA0133','IA1833','IA7161','IA8806',
'IA4735','IA6327','IA8706','IA4894','IA0200','IA2864','IA0364',
'IA7842','IA2789','IA8688','IA5198','IA2203','IA2364',
'IA0000', 'IA4101']

def get_table(sid):
    """
    Return the table which has the data for this siteID
    """
    return "alldata_%s" % (sid.lower()[:2],)

def yrcnt(sid):
  """ Compute the number of years each month will have in the records """
  sts = startts(sid)
  r = [0]*13
  for m in range(1,13):
    ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(month=m,day=1)
    if (ts > _ARCHIVEENDTS):
      r[m] = _ARCHIVEENDTS.year - sts.year
    else:
      r[m] = _ARCHIVEENDTS.year - sts.year + 1

  return r



def climatetable(sid):
  if (startyear(sid) == 1951):
    return "climate51"
  return "climate"

def startts(sid):
  return mx.DateTime.DateTime(startyear(sid),1,1)

def startyear(sid):
    if sid in longterm:
        return 1893
    return 1951

def make_output(nt, station, reportid):
    """ Create and return the output file used for this reportid """
    fn = "/mesonet/share/climodat/reports/%s_%s.txt" % (station, reportid)
    fp = open(fn, 'w')
    fp.write("""# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s 
# Climate Record: %s -> %s (data after %s is preliminary)
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978\n""" % (
    mx.DateTime.now().strftime("%d %b %Y"), 
    startts(station).strftime("%d %b %Y"), _ARCHIVEENDTS.strftime("%d %b %Y"), 
   _QCENDTS.strftime("%d %b %Y"), station, nt.sts[station]["name"]) )
    return fp