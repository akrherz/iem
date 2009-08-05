# Class for building a Network Report for a IEM Access Network

from pyIEM import iemAccess
iemaccess = iemAccess.iemAccess()

class netreport:

  def __init__(self, network, netname, obsday=0, mydate='YESTERDAY', vars=['tmpf', 'dwpf', 'pday']):
    self.network = network
    self.netname = netname
    self.obsday = obsday
    self.db = iemaccess.iemdb
    self.date = mydate
    self.extremes = {}
    self.report = "-" * 65 + "\n"
    self.doPerform()
    self.report += "-" * 65 + "\n"
    if (vars.__contains__('tmpf')):
      self.doVarTime('tmpf', 'max_tmpf', 'max')
      self.printExtreme('max_tmpf', 'High Air Temp[F]')
      self.doVarTime('tmpf', 'min_tmpf', 'min')
      self.printExtreme('min_tmpf', 'Low Air Temp[F]')
    if (vars.__contains__('max_tmpf')):
      self.doVarNoTime('max_tmpf', 'max')
      self.printExtreme('max_tmpf', 'High Air Temp[F]')
    if (vars.__contains__('min_tmpf')):
      self.doVarNoTime('min_tmpf', 'min')
      self.printExtreme('min_tmpf', 'Low Air Temp[F]')
    if (vars.__contains__('dwpf')):
      self.doVarTime('dwpf', 'max_dwpf', 'max')
      self.printExtreme('max_dwpf', 'High Dew Point[F]')
      self.doVarTime('dwpf', 'min_dwpf', 'min')
      self.printExtreme('min_dwpf', 'Low Dew Point[F]')
    if (vars.__contains__('sknt')):
      self.doVarNoTime('max_sknt', 'max')
      self.printExtreme('max_sknt', 'Peak Gust[knots]')
    if (vars.__contains__('gust')):
      self.doVarNoTime('gust', 'max')
      self.printExtreme('gust', 'Peak Gust[knots]')
    if (vars.__contains__('pday')):
      self.doVarNoTime('pday', 'max')
      self.printExtreme('pday', 'Max Rainfall [inch]')
    if (vars.__contains__('snow')):
      self.doVarNoTime('snow', 'max')
      self.printExtreme('snow', 'Max Snowfall [inch]')

  def doPerform(self):
    sql = """
select count(distinct(station)) as cnt, count(*) as obs from 
  (select station, valid from current_log 
   WHERE network = '%s' and local_date(valid) = '%s' 
   GROUP by station, valid) as foo""" % (self.network, self.date)
    rs = self.db.query(sql).dictresult()
    #obshr = float(rs[0]['obs']) / float(self.obsday * int(rs[0]['cnt'])) * 100.0 
    self.report += " %-20.20s Reporting Stations: %s  Obs Received: %s\n" % (self.netname, int(rs[0]['cnt']), int(rs[0]['obs']))

  def doVarTime(self, varcur, varsum, aggf):
    d = {'dbvarcur': varcur, 'dbvarsum': varsum, 'dbdate': self.date,
         'network': self.network, 'aggf': aggf }
    sql = """
select
  count(v) as cnt, min(v) as v, to_char(min(valid), 'HH:MI PM') as otime, station, min(sname) as sname
  from
    (SELECT
       valid, station, %(dbvarcur)s as v, sname from current_log
       WHERE %(dbvarcur)s =
         (SELECT
           %(aggf)s(%(dbvarsum)s) as v from summary
           WHERE %(dbvarsum)s < 120 and %(dbvarsum)s > -40
                 and day = '%(dbdate)s' and 
                 network = '%(network)s')
       and local_date(valid) = '%(dbdate)s' and network = '%(network)s') as foo
  GROUP by station
""" % d

    #print varcur, varsum, aggf, sql
    rs = self.db.query(sql).dictresult()
    self.extremes[varsum] = rs

  def doVarNoTime(self, varsum, aggf):
    d = {'dbvarsum': varsum, 'dbdate': self.date, 'lbound': ' > -40 ',
         'network': self.network, 'aggf': aggf, 'tscol': "to_char(valid, 'HH:MI PM') as otime" }
    s = ['pday', 'snow', 'max_tmpf', 'min_tmpf']
    if (s.__contains__(varsum)): d['tscol'] = "' ' as otime "
    if (self.network == 'IA_COOP' and varsum == 'min_tmpf'):
      d['dbdate'] = 'YESTERDAY'
    if (varsum == 'pday' or varsum == 'snow'):
      d['lbound'] = ' > 0 '
#    sql = """
#    SELECT
#       station, %(dbvarsum)s as v, getsname(station) as sname, 
#       %(tscol)s from summary
#       WHERE %(dbvarsum)s =
#        (SELECT
#           %(aggf)s(%(dbvarsum)s) as v from summary
#           WHERE %(dbvarsum)s < 120 and %(dbvarsum)s %(lbound)s
#           and day = '%(dbdate)s' and network = '%(network)s')
#       and day = '%(dbdate)s' and network = '%(network)s'
#""" % d
    sql = "SELECT station, %(dbvarsum)s as v, getsname(station) as sname, \
        %(tscol)s from current_log WHERE date(valid) = '%(dbdate)s' and \
        network = '%(network)s' and %(dbvarsum)s %(lbound)s ORDER by v DESC \
        LIMIT 10" % d

    print sql
    self.extremes[varsum] = []
    rs = self.db.query(sql).dictresult()
    if (len(rs) == 0):
      return
    maxv = rs[0]['v']
    for i in range(len(rs)):
      v = rs[i]['v']
      if (v != maxv):
        return
      self.extremes[varsum].append( rs[i] )



  def printExtreme(self, var, lbl):
    for i in range(len(self.extremes[var])):
      e = self.extremes[var][i]
      self.report += " %-20.20s: %6.2f [%8.8s] %-5s %s\n" % (lbl, e['v'],
         e['otime'], e['station'],
         e['sname'] )
      lbl = ""
      if (i == 2 and len(self.extremes[var]) > 3):
        self.report += " %-20.20s: %s Other Duplicates Skipped\n" % (lbl, len(self.extremes[var]) - 3)
        return
      
