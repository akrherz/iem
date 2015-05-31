"""
Copy RWIS data from iem database to its final resting home in 'rwis'

The RWIS data is partitioned by UTC timestamp

Run at 0Z and 12Z, provided with a timestamp to process
"""
import psycopg2.extras
import datetime
import pytz
import sys

IEMDB = psycopg2.connect(database="iem", host='iemdb')
RWISDB = psycopg2.connect(database="rwis", host='iemdb')

ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
ts = ts.replace(hour=0, second=0, minute=0, microsecond=0,
                tzinfo=pytz.timezone("UTC"))
ts2 = ts + datetime.timedelta(hours=24)
rcursor = RWISDB.cursor()
# Remove previous entries for this UTC date
rcursor.execute("""DELETE from t%s WHERE valid >= '%s'
    and valid < '%s'""" % (ts.year, ts, ts2))
rcursor.execute("""DELETE from t%s_soil WHERE valid >= '%s'
    and valid < '%s'""" % (ts.year, ts, ts2))
rcursor.execute("""DELETE from t%s_traffic WHERE valid >= '%s'
    and valid < '%s'""" % (ts.year, ts, ts2))
rcursor.close()

# Always delete stuff 3 or more days old from iemaccess
icursor = IEMDB.cursor()
icursor.execute("""DELETE from rwis_traffic_data_log WHERE
  valid < ('TODAY'::date - '3 days'::interval)""")
icursor.execute("""DELETE from rwis_soil_data_log WHERE
  valid < ('TODAY'::date - '3 days'::interval)""")
icursor.close()

# Get traffic obs from access
icursor = IEMDB.cursor(cursor_factory=psycopg2.extras.DictCursor)
icursor.execute(""" SELECT l.nwsli as station, s.lane_id, d.* from
   rwis_traffic_data_log d, rwis_locations l, rwis_traffic_sensors s
   WHERE s.id = d.sensor_id and valid >= '%s' and valid < '%s'
   and s.location_id = l.id""" % (ts, ts2))
rows = icursor.fetchall()
if len(rows) == 0:
    print 'No RWIS traffic found between %s and %s' % (ts, ts2)
icursor.close()

# Write to archive
rcursor = RWISDB.cursor()
rcursor.executemany("""INSERT into t""" + repr(ts.year) + """_traffic
    (station, valid,
    lane_id, avg_speed, avg_headway, normal_vol, long_vol, occupancy) VALUES (
    %(station)s,%(valid)s,
    %(lane_id)s, %(avg_speed)s, %(avg_headway)s, %(normal_vol)s,
    %(long_vol)s, %(occupancy)s)
    """, rows)
rcursor.close()


# Get soil obs from access
icursor = IEMDB.cursor(cursor_factory=psycopg2.extras.DictCursor)
sql = """SELECT l.nwsli as station, d.valid,
     max(case when sensor_id = 0 then temp else null end) as s0temp,
     max(case when sensor_id = 1 then temp else null end) as s1temp,
     max(case when sensor_id = 2 then temp else null end) as s2temp,
     max(case when sensor_id = 3 then temp else null end) as s3temp,
     max(case when sensor_id = 4 then temp else null end) as s4temp,
     max(case when sensor_id = 5 then temp else null end) as s5temp,
     max(case when sensor_id = 6 then temp else null end) as s6temp,
     max(case when sensor_id = 7 then temp else null end) as s7temp,
     max(case when sensor_id = 8 then temp else null end) as s8temp,
     max(case when sensor_id = 9 then temp else null end) as s9temp,
     max(case when sensor_id = 10 then temp else null end) as s10temp,
     max(case when sensor_id = 11 then temp else null end) as s11temp,
     max(case when sensor_id = 12 then temp else null end) as s12temp,
     max(case when sensor_id = 13 then temp else null end) as s13temp,
     max(case when sensor_id = 14 then temp else null end) as s14temp
     from rwis_soil_data_log d, rwis_locations l
     WHERE valid >= '%s' and valid < '%s' and d.location_id = l.id
     GROUP by station, valid""" % (ts, ts2)
icursor.execute(sql)
rows = icursor.fetchall()
if len(rows) == 0:
    print 'No RWIS soil obs found between %s and %s' % (ts, ts2)
icursor.close()

# Write to RWIS Archive
rcursor = RWISDB.cursor()
rcursor.executemany("""INSERT into t""" + repr(ts.year) + """_soil
    (station, valid,
    s0temp, s1temp, s2temp, s3temp, s4temp, s5temp, s6temp, s7temp,
    s8temp, s9temp, s10temp, s11temp, s12temp, s13temp, s14temp) VALUES (
    %(station)s,%(valid)s,
    %(s0temp)s, %(s1temp)s, %(s2temp)s, %(s3temp)s, %(s4temp)s, %(s5temp)s,
    %(s6temp)s, %(s7temp)s,
    %(s8temp)s, %(s9temp)s, %(s10temp)s, %(s11temp)s, %(s12temp)s,
    %(s13temp)s, %(s14temp)s)
    """, rows)
rcursor.close()

# Get regular obs from Access
icursor = IEMDB.cursor(cursor_factory=psycopg2.extras.DictCursor)
# Since we store drct in the RWIS archive as NaN, we better make sure
# we don't attempt to use these values as it will error out
icursor.execute("""update current_log set drct = null where drct = 'NaN'""")
sql = """SELECT c.*, t.id as station from current_log c, stations t
    WHERE valid >= '%s' and valid < '%s'
      and t.network ~* 'RWIS' and t.iemid = c.iemid""" % (ts, ts2)
icursor.execute(sql)
rows = icursor.fetchall()
if len(rows) == 0:
    print 'No RWIS obs found between %s and %s' % (ts, ts2)
icursor.close()

# Write to RWIS Archive
rcursor = RWISDB.cursor()
rcursor.executemany("""INSERT into t""" + repr(ts.year) + """
    (station, valid, tmpf,
    dwpf, drct, sknt, tfs0, tfs1, tfs2, tfs3, subf, gust, tfs0_text,
    tfs1_text, tfs2_text, tfs3_text, pcpn, vsby) VALUES (%(station)s,
    %(valid)s,%(tmpf)s,%(dwpf)s,%(drct)s,%(sknt)s,%(tsf0)s,
    %(tsf1)s,%(tsf2)s,%(tsf3)s,%(rwis_subf)s,%(gust)s,%(scond0)s,
    %(scond1)s,%(scond2)s,%(scond3)s,%(pday)s,%(vsby)s)""", rows)
rcursor.close()


RWISDB.commit()
IEMDB.commit()
RWISDB.close()
IEMDB.close()
