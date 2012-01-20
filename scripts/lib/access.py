"""
 This hacky code is an interface to the iem obs database for current and summary data
 TODO: make it async
 
 $Id: $:
"""

import traceback
import mx.DateTime
import psycopg2.extras
import mesonet

class mydata(dict):
    
    def __getitem__(self, key):
        """
        Over-ride getitem so that the sql generated is proper
        """
        val = self.get(key)
        if val is None and key == 'tzname':
            return "'America/Chicago'"
        if val is None:
            return 'null'
        if type(val) == type(''):
            return "'%s'" % (val,)
        return val

def get_network(network, dbconn, valid=mx.DateTime.now()):
    """
    Return a dict of Ob  for the given network
    @param network string network name
    @param dbconn database connection
    @param valid optional timestamp to use to fetch obs for!
    @return dict of obs
    """
    obs = {}
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
    SELECT c.*, s.*, t.id, t.name as sname from current c, summary_%s s, stations t WHERE
    t.iemid = s.iemid and s.iemid = c.iemid and t.network = '%s' and
    s.day = '%s'
    """ % (valid.year, network, valid.strftime("%Y-%m-%d")))
    for row in cursor:
        obs[ row['id'] ] = Ob(row['id'], network)
        for key in row.keys():
            obs[ row['id'] ].data[key] = row[key]
        obs[ row['id'] ].data['ts'] = mx.DateTime.strptime(str(row['valid'])[:16], "%Y-%m-%d %H:%M")
    cursor.close()
    return obs

def get_network_recent(network, dbconn, valid, window=10):
    """
    Return a dict of Ob for recent data in current_log
    @param network string network name
    @param dbconn database connection
    @param valid timestamp to use to fetch obs for!
    @param window observation window to look for obs
    @return dict of obs
    """
    obs = {}
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
    SELECT c.*, t.id from current_log c JOIN stations t ON (t.iemid = c.iemid) WHERE
    t.network = %s and c.valid BETWEEN %s and %s::timestamptz + '%s minutes'::interval ORDER by valid ASC
    """ , (network, valid.strftime("%Y-%m-%d %H:%M"), valid.strftime("%Y-%m-%d %H:%M"), window))
    for row in cursor:
        id = row['id']
        if obs.has_key(id):
            continue
        obs[ row['id'] ] = Ob(row['id'], network)
        for key in row.keys():
            obs[ row['id'] ].data[key] = row[key]
        obs[ row['id'] ].data['ts'] = mx.DateTime.strptime(str(row['valid'])[:16], "%Y-%m-%d %H:%M")
    cursor.close()
    return obs

class Ob(object):

    def __init__(self, station, network, txn=None):
        """
        Construct an Ob instance from
        @param station string station
        @param network string network
        """
        self.data = mydata({'station': station, 'network': network})
        self.txn = txn

    def load_and_compare(self, db=None):
        """
        We want to load up current entry from the database and see what
        we have
        """
        # Don't check the database, if we have nothing to compare it against
        if self.data.get('valid') is None:
            return False

        # This will have some issues around the new year, sigh
        sql = """SELECT c.*, s.* from current c, summary_%s s, stations t WHERE
            c.iemid = s.iemid and c.iemid = t.iemid and
            s.day = date('%s'::timestamptz at time zone t.tzname) and 
            t.id = '%s' and t.network = '%s' """ % ( self.data.get('valid').year, 
          self.data.get('valid').strftime("%Y-%m-%d %H:%M"), self.data.get('station'),
          self.data.get('network') )
        if self.txn is not None:
            self.txn.execute(sql)
            if self.txn.rowcount == 0:
                return False
            row = self.txn.fetchone()
        else:
            rs = db.query(sql).dictresult()
            if len(rs) == 0:
                return False
            row = rs[0]

        self.data['old_valid'] = mx.DateTime.strptime(str(row['valid'])[:16], "%Y-%m-%d %H:%M")
        if self.data['valid'] == self.data['old_valid']: # Same Ob!
            for key in row.keys():
                if row[key] is not None and key not in ['valid','network','station','geom']:
                    self.data[key] = row[key]
        # We can always load up the summary obs, since we queried for the local ob summary?
        else:
            for key in ['pmonth', 'max_tmpf', 'min_tmpf', 'max_sknt', 'max_gust', 'max_gust_ts',
                        'max_sknt_ts', 'max_drct']:
                self.data[key] = row[key]
        return True

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
        if self.txn is not None:
            return self.txn.execute(sql)
        if dbpool != None:
            dbpool.runOperation( sql )
        else:
            try:
                db.query( sql )
            except:
                print sql
                traceback.print_exc()

    def updateDatabasePeakWind(self, db, gdata, dbpool=None):
        table = "summary_%s" % (self.data['valid'].year,)
        sql = """UPDATE """+ table +""" s SET 
     max_gust = 
      (CASE WHEN max_gust < '%(peak_gust)s' THEN '%(peak_gust)s' ELSE max_gust END),
     max_gust_ts = 
      (CASE WHEN max_gust < '%(peak_gust)s' THEN '%(peak_ts)s' ELSE max_gust_ts END),
     max_drct = 
      (CASE WHEN max_gust < '%(peak_gust)s' THEN '%(peak_drct)s' ELSE max_drct END)
      FROM stations t
     WHERE t.iemid = s.iemid and t.id = '%(stationID)s' and t.network = '%(network)s' 
     and day = date('%(peak_ts)s'::timestamptz at time zone t.tzname)""" % gdata
        self.execQuery(sql, db, dbpool)


    def updateDatabaseSummaryTemps(self, db=None, dbpool=None):
        table = "summary_%s" % (self.data['valid'].year,)
        sql = """UPDATE """+ table +""" s SET 
              max_tmpf = 
       (CASE WHEN max_tmpf < %(max_tmpf)s THEN %(max_tmpf)s ELSE max_tmpf END),
      min_tmpf = 
       (CASE WHEN min_tmpf > %(min_tmpf)s THEN %(min_tmpf)s ELSE min_tmpf END) 
       FROM stations t
      WHERE t.iemid = s.iemid and t.id = %(station)s and 
      day = date('%(valid)s'::timestamptz at time zone t.tzname) 
      and t.network = %(network)s""" % self.data
        self.execQuery(sql , db, dbpool)

    def update_summary(self, db=None, dbpool=None):
        table = "summary_%s" % (self.data['valid'].year,)
        sql = """UPDATE """+ table +""" s SET 
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
     max_drct = (CASE WHEN %(max_drct)s > 0 THEN %(max_drct)s ELSE max_drct END), 
     max_srad =
      (CASE WHEN max_srad < %(max_srad)s THEN %(max_srad)s ELSE max_srad END), 
     snow = %(snow)s, snowd = %(snowd)s, snoww = %(snoww)s 
     FROM stations t
     WHERE t.iemid = s.iemid and t.id = %(station)s 
     and day = date('%(valid)s'::timestamptz at time zone t.tzname) 
     and t.network = %(network)s """ % self.data
        self.execQuery(sql, db, dbpool)

    def update_current(self, db=None, dbpool=None):
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
       gust = %(gust)s, alti = %(alti)s, presentwx = %(presentwx)s,
       rstage = %(rstage)s, ozone = %(ozone)s, co2 = %(co2)s, 
       skyc1 = %(skyc1)s, skyl1 = %(skyl1)s, 
       skyc2 = %(skyc2)s, skyl2 = %(skyl2)s, 
       skyc3 = %(skyc3)s, skyl3 = %(skyl3)s, 
       skyc4 = %(skyc4)s, skyl4 = %(skyl4)s,
       p03i = %(p03i)s, p06i = %(p06i)s, p24i = %(p24i)s,
       max_tmpf_6hr = %(max_tmpf_6hr)s, min_tmpf_6hr = %(min_tmpf_6hr)s,
       max_tmpf_24hr = %(max_tmpf_24hr)s, min_tmpf_24hr = %(min_tmpf_24hr)s,
       valid = '%(valid)s', pcounter = %(pcounter)s, discharge = %(discharge)s ,
       raw = (CASE WHEN length(raw) > length(%(raw)s) and valid = '%(valid)s'
          THEN raw ELSE %(raw)s END)
          FROM stations t
       WHERE t.iemid = c.iemid and t.id = %(station)s and t.network = %(network)s """ % self.data
        self.execQuery(sql, db, dbpool)
        
    def insert_currentlog(self, db=None, dbpool=None):
        sql = """INSERT into current_log(iemid, tmpf, dwpf, 
       phour, tsf0, tsf1, tsf2, 
       tsf3, rwis_subf, pres, drct, sknt, pday, 
       scond0, scond1, relh, scond2, scond3, srad, 
       c1smv, c2smv, c3smv, c4smv, c5smv, vsby, 
       c1tmpf, c2tmpf, c3tmpf, c4tmpf, c5tmpf, 
       gust, raw, alti, rstage, ozone, co2, valid, presentwx,
       p03i, p06i, p24i, max_tmpf_6hr, min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr,
       skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, pcounter, discharge) VALUES 
        ((SELECT iemid from stations where id = %(station)s and network = %(network)s), 
        %(tmpf)s, %(dwpf)s, 
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
         '%(valid)s', %(presentwx)s,
         %(p03i)s, %(p06i)s, %(p24i)s,
         %(max_tmpf_6hr)s, %(min_tmpf_6hr)s, %(max_tmpf_24hr)s, %(min_tmpf_24hr)s,
         %(skyc1)s, %(skyc2)s, %(skyc3)s, %(skyc4)s,
                   %(skyl1)s, %(skyl2)s, %(skyl3)s, %(skyl4)s, 
                   %(pcounter)s, %(discharge)s)  """ % self.data
        self.execQuery(sql, db, dbpool)


    def updateDatabase(self, db=None, dbpool=None):
        """
        Update the Access database with this observation info
        """
        # We can always update the summary database
        self.update_summary(db, dbpool)

        # We can update current if old_ts is not set or ts > old_ts
        if self.data.get('old_valid') is None or self.data.get('valid') >= self.data.get('old_valid'):
            self.update_current(db, dbpool)
        else:
            self.insert_currentlog(db, dbpool)

    def metar(self):
        """
        Return a METAR representation of this observation :)
        """
        s = ""
        # First up, is the ID, which needs to be 3 or 4 char :(
        mid = self.data.get('station')
        if len(self.data.get('station')) > 4:
            mid = 'Q%s' % (self.data.get('station')[1:4])
        # Metar Time
        mtrts = self.data.get('ts').gmtime().strftime("%d%H%MZ")
        # Wind Direction
        mdir = self.data.get('drct', 0)
        if mdir == 360:
            mdir = 0
        mwind = "%03i%02iKT" % (mdir, self.data.get('sknt', 0) )
        # Temperature
        mtmp = "%s/%s" % (mesonet.metar_tmpf(self.data.get('tmpf')), 
                          mesonet.metar_tmpf(self.data.get('dwpf')))
        # Altimeter
        malti = "A%04i" % (self.data.get('pres',0) * 100.0,)
        # Remarks
        tgroup = "T%s%s" % (mesonet.metar_tmpf_tgroup(self.data.get('tmpf')), 
                            mesonet.metar_tmpf_tgroup(self.data.get('dwpf')))
        # Phour
        phour = "P%04i" % (self.data.get('phour',0),)
        # Pday
        pday = "7%04i" % (self.data.get('pday',0),)
        return "%s %s %s %s RMK %s %s %s %s=\015\015\012" % (mid, mtrts, mwind, mtmp, 
                                    malti, tgroup, phour, pday)
