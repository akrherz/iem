import traceback
import mx.DateTime

class mydata(dict):
    
    def __getitem__(self, key):
        """
        Over-ride getitem so that the sql generated is proper
        """
        val = self.get(key)
        if val is None:
            return 'null'
        if type(val) == type(''):
            return "'%s'" % (val,)
        return val

class Ob(object):

    def __init__(self, station, network):
        """
        Construct an Ob instance from
        @param station string station
        @param network string network
        """
        self.data = mydata({'station': station, 'network': network})

    def load_and_compare(self, db):
        """
        We want to load up current entry from the database and see what
        we have
        """
        if self.data.get('valid') is None:
            return False

        rs = db.query("""SELECT c.*, s.* from current c, summary_%s s WHERE 
          c.station = '%s' and s.day = 'TODAY' and 
          c.station = s.station and c.network = s.network and
          c.network = '%s' """ % (
          self.data.get('valid').year, self.data.get('station'), 
          self.data.get('network') ) ).dictresult()
        if len(rs) == 0:
            print "No rows found for station: %(station)s network: %(network)s" % self.data
            return False

        self.data['old_valid'] = mx.DateTime.strptime(rs[0]['valid'][:16], 
                              "%Y-%m-%d %H:%M")
        if self.data['valid'] == self.data['old_valid']: # Same Ob!
            for key in rs[0].keys():
                if rs[0][key] is not None and key not in ['valid','network','station','geom']:
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
        self.data['valid'] = ts
        
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
        table = "summary_%s" % (self.data['valid'].year,)
        sql = """UPDATE """+ table +""" c SET 
	pday = 
      (CASE WHEN %(pday)s >= -1 THEN %(pday)s ELSE pday END)::numeric, 
     pmonth = 
      (CASE WHEN %(pmonth)s >= -1 THEN %(pmonth)s ELSE pmonth END)::numeric, 
     max_tmpf =
      (CASE WHEN max_tmpf < %(tmpf)s THEN %(tmpf)s ELSE max_tmpf END),
     min_tmpf =
      (CASE WHEN min_tmpf > %(tmpf)s THEN %(tmpf)s ELSE min_tmpf END), 
     max_dwpf =
      (CASE WHEN max_dwpf < %(dwpf)s THEN %(dwpf)s ELSE max_dwpf END),
     min_dwpf =
      (CASE WHEN min_dwpf > %(dwpf)s THEN %(dwpf)s ELSE min_dwpf END), 
     max_sknt =
      (CASE WHEN max_sknt < %(sknt)s THEN %(sknt)s ELSE max_sknt END), 
     max_sknt_ts =
      (CASE WHEN max_sknt < %(sknt)s THEN '%(valid)s' ELSE max_sknt_ts END), 
     max_gust =
      (CASE WHEN max_gust < %(gust)s THEN %(gust)s ELSE max_gust END), 
     max_gust_ts =
      (CASE WHEN max_gust < %(gust)s THEN '%(valid)s' ELSE max_gust_ts END), 
     max_drct =
      (CASE WHEN %(max_drct)s > 0 THEN %(max_drct)s ELSE max_drct END), 
     max_srad =
      (CASE WHEN max_srad < %(max_srad)s THEN %(max_srad)s ELSE max_srad END), 
     snow = %(snow)s, snowd = %(snowd)s, snoww = %(snoww)s 
     WHERE station = %(station)s and day = '%(valid)s'::date 
     and network = %(network)s """ % self.data
        self.execQuery(sql, db, dbpool)

    def update_current(self, db, dbpool):
        sql = """UPDATE current c SET tmpf = %(tmpf)s, dwpf = %(dwpf)s, 
	phour = 
      (CASE WHEN %(phour)s >= -1 THEN %(phour)s ELSE phour END)::numeric, 
       tsf0 = %(tsf0)s, tsf1 = %(tsf1)s, tsf2 = %(tsf2)s, 
       tsf3 = %(tsf3)s, rwis_subf = %(rwis_subf)s, pres = %(pres)s, 
       drct = %(drct)s, sknt = %(sknt)s, pday = %(pday)s, 
       scond0 = %(scond0)s, scond1 = %(scond1)s, relh = %(relh)s, 
       scond2 = %(scond2)s, scond3 = %(scond3)s, srad = %(srad)s, 
       c1smv = %(c1smv)s, c2smv = %(c2smv)s, c3smv = %(c3smv)s, 
       c4smv = %(c4smv)s, c5smv = %(c5smv)s, vsby = %(vsby)s, 
       c1tmpf = %(c1tmpf)s, c2tmpf = %(c2tmpf)s, c3tmpf = %(c3tmpf)s, 
       c4tmpf = %(c4tmpf)s, c5tmpf = %(c5tmpf)s, pmonth = %(pmonth)s, 
       gust = %(gust)s, alti = %(alti)s, 
       rstage = %(rstage)s, ozone = %(ozone)s, co2 = %(co2)s, 
       skyc1 = %(skyc1)s, skyl1 = %(skyl1)s, 
       skyc2 = %(skyc2)s, skyl2 = %(skyl2)s, 
       skyc3 = %(skyc3)s, skyl3 = %(skyl3)s, 
       valid = '%(valid)s',
       raw = (CASE WHEN length(raw) > length(%(raw)s) and valid = '%(valid)s'
          THEN raw ELSE %(raw)s END)
       WHERE station = %(station)s and network = %(network)s """ % self.data
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
        (%(station)s, %(network)s, (select geom from current 
        WHERE station = %(station)s and network = %(network)s), %(tmpf)s, %(dwpf)s, 
         (CASE WHEN %(phour)s >= -1 THEN %(phour)s ELSE null END)::numeric, 
         %(tsf0)s,%(tsf1)s,%(tsf2)s, 
         %(tsf3)s,%(rwis_subf)s,%(pres)s, 
         %(drct)s,%(sknt)s,%(pday)s, 
         %(scond0)s,%(scond1)s,%(relh)s, 
         %(scond2)s,%(scond3)s,%(srad)s, 
         %(c1smv)s,%(c2smv)s,%(c3smv)s, 
         %(c4smv)s,%(c5smv)s,%(vsby)s, 
         %(c1tmpf)s,%(c2tmpf)s,%(c3tmpf)s, 
         %(c4tmpf)s,%(c5tmpf)s, 
         %(gust)s,%(raw)s,%(alti)s, 
         %(rstage)s, %(ozone)s,%(co2)s, 
         '%(valid)s', %(skyc1)s, %(skyc2)s, %(skyc3)s, 
                   %(skyl1)s, %(skyl2)s, %(skyl3)s)  """ % self.data
        self.execQuery(sql, db, dbpool)

    def updateDatabase(self, db, dbpool=None):
        """
        Update the Access database with this observation info
        """
        # We can always update the summary database
        self.update_summary(db, dbpool)

        # We can update current if old_ts is not set or ts > old_ts
        if self.data.get('old_valid') is None or self.data.get('valid') > self.data.get('old_valid'):
            self.update_current(db, dbpool)
        else:
            self.insert_currentlog(db, dbpool)
