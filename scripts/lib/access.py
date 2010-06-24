import traceback
import mx.DateTime

class Ob(object):

    def __init__(self, stationID, network=None):
        """
        Construct Ob based on stationID and optional network
        """
        self.stationID = stationID
        self.network = network
        self.data = {
           'tmpf': None, 'dwpf': None, 'tsf0': None, 'tsf1': None, 
           'tsf2': None, 'tsf3': None, 'rwis_subf': None, 'vsby': None,
           'drct': None, 'sknt': None, 'scond0': None, 'srad': None,
           'scond1': None, 'scond2': None, 'scond3': None, 
            'ozone': None, 'co2': None,
            'skyc1': None, 'skyl1': None,
            'skyc2': None, 'skyl2': None,
             'skyc3': None, 'skyl3': None,
             'pday': None, 'pmonth': None, 'pres': None, 'relh': None,
             'c1smv': None, 'c2smv': None, 'c3smv': None, 'rstage': None,
             'c4smv': None, 'c5smv': None, 'gust': None, 'alti': None,
             'max_tmpf': None, 'min_tmpf': 99, 'snow': None, 'snowd': None,
             'c1tmpf': None, 'c2tmpf': None, 'c3tmpf': None, 'snoww': None,
             'c4tmpf': None, 'c5tmpf': None, 'phour': None, 'raw': None,
             'max_drct': None, 'max_srad': None, 'year': None,
	         'stationID': stationID, 'network': network, 'ts': None, 
             'old_ts': None
         }

    def networkcheck(self):
        """
        return a string if we can also query against a network
        """
        if self.network is None:
            return ""
        return " and c.network = '%s' " % (self.network,)

    def load_and_compare(self, db):
        """
        We want to load up current entry from the database and see what
        we have
        """
        if self.data['ts'] is None:
            return

        rs = db.query("""SELECT c.*, s.* from current c, summary_%s s WHERE 
          c.station = '%s' and s.day = 'TODAY' and 
          c.station = s.station and c.network = s.network %s""" % (
          self.stationID, self.networkcheck() ) ).dictresult()
        if len(rs) == 0:
            print "No rows found for stationID: %s network: %s" % (
              self.stationID, self.data['network'])
            return
        self.data['network'] = rs[0]['network']
        self.data['old_ts'] = mx.DateTime.strptime(rs[0]['valid'][:16], 
                              "%Y-%m-%d %H:%M")
        if self.data['ts'] == self.data['old_ts']: # Same Ob!
            for key in rs[0].keys():
                if rs[0][key] is not None:
                    self.data[key] = rs[0][key]

    def setObTimeGMT(self, ts):
        """
        Set the observation valid time based on a GMT time
        """
        self.setObTime( ts.localtime() )

    def setObTime(self, ts):
        """
        Set the observation time based on a time object
        """
        self.data['ts'] = ts
        self.data['year'] = ts.year

    def execQuery(self, sql, db, dbpool):
        """
        Helper function for select/update queries
        """
        if dbpool != None:
            dbpool.runOperation( sql )
        else:
            try:
                db.query( sql )
            except:
                print sql
                traceback.print_exc()

    def update_summary(self, db, dbpool):
        sql = """UPDATE summary_%(year)s c SET 
	pday = 
      (CASE WHEN %(pday)s >= -1 THEN %(pday)s ELSE pday END), 
     pmonth = 
      (CASE WHEN %(pmonth)s >= -1 THEN %(pmonth)s ELSE pmonth END), 
     max_tmpf =
      (CASE WHEN max_tmpf < %(tmpf)s THEN %(tmpf)s ELSE max_tmpf END),
     min_tmpf =
      (CASE WHEN (min_tmpf > %(tmpf)s and %(tmpf)s > None) THEN %(tmpf)s ELSE min_tmpf END), 
     max_dwpf =
      (CASE WHEN max_dwpf < %(dwpf)s THEN %(dwpf)s ELSE max_dwpf END),
     min_dwpf =
      (CASE WHEN (min_dwpf > %(dwpf)s and %(dwpf)s > None) THEN %(dwpf)s ELSE min_dwpf END), 
     max_sknt =
      (CASE WHEN max_sknt < %(sknt)s THEN %(sknt)s ELSE max_sknt END), 
     max_sknt_ts =
      (CASE WHEN max_sknt < %(sknt)s THEN '%(ts)s' ELSE max_sknt_ts END), 
     max_gust =
      (CASE WHEN max_gust < %(gust)s THEN %(gust)s ELSE max_gust END), 
     max_gust_ts =
      (CASE WHEN max_gust < %(gust)s THEN '%(ts)s' ELSE max_gust_ts END), 
     max_drct =
      (CASE WHEN %(max_drct)s > 0 THEN %(max_drct)s ELSE max_drct END), 
     max_srad =
      (CASE WHEN max_srad < %(max_srad)s THEN %(max_srad)s ELSE max_srad END), 
     snow = %(snow)s, snowd = %(snowd)s, snoww = %(snoww)s 
     WHERE station = '%(stationID)s' and day = '%(ts)s'::date """ % self.data
        sql = sql + self.networkcheck()
        sql = sql.replace("None", "Null").replace("'Null'", "Null")
        self.execQuery(sql, db, dbpool)

    def update_current(self, db, dbpool):
        sql = """UPDATE current c SET tmpf = %(tmpf)s, dwpf = %(dwpf)s, 
	phour = 
      (CASE WHEN %(phour)s >= -1 THEN %(phour)s ELSE phour END), 
       tsf0 = %(tsf0)s, tsf1 = %(tsf1)s, tsf2 = %(tsf2)s, 
       tsf3 = %(tsf3)s, rwis_subf = %(rwis_subf)s, pres = %(pres)s, 
       drct = %(drct)s, sknt = %(sknt)s, pday = %(pday)s, 
       scond0 = '%(scond0)s', scond1 = '%(scond1)s', relh = %(relh)s, 
       scond2 = '%(scond2)s', scond3 = '%(scond3)s', srad = %(srad)s, 
       c1smv = %(c1smv)s, c2smv = %(c2smv)s, c3smv = %(c3smv)s, 
       c4smv = %(c4smv)s, c5smv = '%(c5smv)s', vsby = '%(vsby)s', 
       c1tmpf = %(c1tmpf)s, c2tmpf = %(c2tmpf)s, c3tmpf = %(c3tmpf)s, 
       c4tmpf = %(c4tmpf)s, c5tmpf = %(c5tmpf)s, pmonth = %(pmonth)s, 
       gust = %(gust)s, alti = %(alti)s, 
       rstage = %(rstage)s, ozone = %(ozone)s, co2 = %(co2)s, 
       skyc1 = '%(skyc1)s', skyl1 = %(skyl1)s, 
       skyc2 = '%(skyc2)s', skyl2 = %(skyl2)s, 
       skyc3 = '%(skyc3)s', skyl3 = %(skyl3)s, 
       valid = '%(ts)s',
       raw = (CASE WHEN length(raw) > length('%(raw)s') and valid = '%(ts)s' 
          THEN raw ELSE '%(raw)s' END)
       WHERE station = '%(stationID)s'""" % self.data
        sql = sql + self.networkcheck()
        sql = sql.replace("None", "Null").replace("'Null'", "Null")
        self.execQuery(sql, db, dbpool)

    def insert_currentlog(self, db, dbpool):
        sql = """INSERT into current_log(station, network, geom, tmpf, dwpf, 
       phour, tsf0, tsf1, tsf2, 
       tsf3, rwis_subf, pres, drct, sknt, pday, 
       scond0, scond1, relh, scond2, scond3, srad, 
       c1smv, c2smv, c3smv, c4smv, c5smv, vsby, 
       c1tmpf, c2tmpf, c3tmpf, c4tmpf, c5tmpf, 
       gust, raw, alti, rstage, ozone, co2, valid, 
       skyc1, skyc2, skyc3, skyl1, skyl2, skyl3) VALUES 
        ('%(stationID)s', '%(network)s', (select geom from current WHERE station = '%(stationID)s' and network = '%(network)s'), %(tmpf)s, %(dwpf)s, 
         (CASE WHEN %(phour)s >= -1 THEN %(phour)s ELSE None END), 
         %(tsf0)s,%(tsf1)s,%(tsf2)s, 
         %(tsf3)s,%(rwis_subf)s,%(pres)s, 
         %(drct)s,%(sknt)s,%(pday)s, 
         '%(scond0)s','%(scond1)s',%(relh)s, 
         '%(scond2)s','%(scond3)s',%(srad)s, 
         %(c1smv)s,%(c2smv)s,%(c3smv)s, 
         %(c4smv)s,%(c5smv)s,%(vsby)s, 
         %(c1tmpf)s,%(c2tmpf)s,%(c3tmpf)s, 
         %(c4tmpf)s,%(c5tmpf)s, 
         %(gust)s,'%(raw)s',%(alti)s, 
         %(rstage)s, %(ozone)s,%(co2)s, 
         '%(ts)s', '%(skyc1)s', '%(skyc2)s', '%(skyc3)s', 
                   %(skyl1)s, %(skyl2)s, %(skyl3)s)  """ % self.data
        sql = sql + self.networkcheck()
        sql = sql.replace("None", "Null").replace("'Null'", "Null")
        self.execQuery(sql, db, dbpool)

    def updateDatabase(self, db, dbpool=None):
        """
        Update the Access database with this observation info
        """
        # We can always update the summary database
        self.update_summary(db, dbpool)

        # We can update current if old_ts is not set or ts > old_ts
        if (self.data['old_ts'] is None or 
            self.data['ts'] > self.data['old_ts']):
            self.update_current(db, dbpool)
        else:
            self.insert_currentlog(db, dbpool)
