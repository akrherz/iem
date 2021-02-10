"""
Copy RWIS data from iem database to its final resting home in 'rwis'

The RWIS data is partitioned by UTC timestamp

Run at 0Z and 12Z, provided with a timestamp to process
"""
import datetime
import sys

import psycopg2.extras
from pyiem.util import get_dbconn, utc


def main(argv):
    """Go main"""
    iemdb = get_dbconn("iem")
    rwisdb = get_dbconn("rwis")

    ts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    ts2 = ts + datetime.timedelta(hours=24)
    rcursor = rwisdb.cursor()
    # Remove previous entries for this UTC date
    for suffix in ["", "_soil", "_traffic"]:
        rcursor.execute(
            f"DELETE from t{ts.year}{suffix} WHERE valid >= %s and valid < %s",
            (ts, ts2),
        )
    rcursor.close()

    # Always delete stuff 3 or more days old from iemaccess
    icursor = iemdb.cursor()
    icursor.execute(
        "DELETE from rwis_traffic_data_log WHERE "
        "valid < ('TODAY'::date - '3 days'::interval)"
    )
    icursor.execute(
        "DELETE from rwis_soil_data_log WHERE "
        "valid < ('TODAY'::date - '3 days'::interval)"
    )
    icursor.close()

    # Get traffic obs from access
    icursor = iemdb.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute(
        """SELECT l.nwsli as station, s.lane_id, d.* from
       rwis_traffic_data_log d, rwis_locations l, rwis_traffic_sensors s
       WHERE s.id = d.sensor_id and valid >= '%s' and valid < '%s'
       and s.location_id = l.id"""
        % (ts, ts2)
    )
    rows = icursor.fetchall()
    if not rows:
        print("No RWIS traffic found between %s and %s" % (ts, ts2))
    icursor.close()

    # Write to archive
    rcursor = rwisdb.cursor()
    rcursor.executemany(
        f"""INSERT into t{ts.year}_traffic
        (station, valid,
        lane_id, avg_speed, avg_headway, normal_vol, long_vol, occupancy)
        VALUES (%(station)s,%(valid)s,
        %(lane_id)s, %(avg_speed)s, %(avg_headway)s, %(normal_vol)s,
        %(long_vol)s, %(occupancy)s)
        """,
        rows,
    )
    rcursor.close()

    # Get soil obs from access
    icursor = iemdb.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT l.nwsli as station, d.valid,
         max(case when sensor_id = 1 then temp else null end) as tmpf_1in,
         max(case when sensor_id = 3 then temp else null end) as tmpf_3in,
         max(case when sensor_id = 6 then temp else null end) as tmpf_6in,
         max(case when sensor_id = 9 then temp else null end) as tmpf_9in,
         max(case when sensor_id = 12 then temp else null end) as tmpf_12in,
         max(case when sensor_id = 18 then temp else null end) as tmpf_18in,
         max(case when sensor_id = 24 then temp else null end) as tmpf_24in,
         max(case when sensor_id = 30 then temp else null end) as tmpf_30in,
         max(case when sensor_id = 36 then temp else null end) as tmpf_36in,
         max(case when sensor_id = 42 then temp else null end) as tmpf_42in,
         max(case when sensor_id = 48 then temp else null end) as tmpf_48in,
         max(case when sensor_id = 54 then temp else null end) as tmpf_54in,
         max(case when sensor_id = 60 then temp else null end) as tmpf_60in,
         max(case when sensor_id = 66 then temp else null end) as tmpf_66in,
         max(case when sensor_id = 72 then temp else null end) as tmpf_72in
         from rwis_soil_data_log d, rwis_locations l
         WHERE valid >= '%s' and valid < '%s' and d.location_id = l.id
         GROUP by station, valid""" % (
        ts,
        ts2,
    )
    icursor.execute(sql)
    rows = icursor.fetchall()
    if not rows:
        print("No RWIS soil obs found between %s and %s" % (ts, ts2))
    icursor.close()

    # Write to RWIS Archive
    rcursor = rwisdb.cursor()
    rcursor.executemany(
        f"""INSERT into t{ts.year}_soil
        (station, valid,
        tmpf_1in, tmpf_3in, tmpf_6in, tmpf_9in, tmpf_12in, tmpf_18in,
        tmpf_24in, tmpf_30in, tmpf_36in, tmpf_42in, tmpf_48in, tmpf_54in,
        tmpf_60in, tmpf_66in, tmpf_72in) VALUES (
        %(station)s,%(valid)s,
        %(tmpf_1in)s, %(tmpf_3in)s, %(tmpf_6in)s, %(tmpf_9in)s, %(tmpf_12in)s,
        %(tmpf_18in)s, %(tmpf_24in)s, %(tmpf_30in)s, %(tmpf_36in)s,
        %(tmpf_42in)s, %(tmpf_48in)s, %(tmpf_54in)s, %(tmpf_60in)s,
        %(tmpf_66in)s, %(tmpf_72in)s)
        """,
        rows,
    )
    rcursor.close()

    # Get regular obs from Access
    icursor = iemdb.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Since we store drct in the RWIS archive as NaN, we better make sure
    # we don't attempt to use these values as it will error out
    icursor.execute("update current_log set drct = null where drct = 'NaN'")
    sql = """SELECT c.*, t.id as station from current_log c, stations t
        WHERE valid >= '%s' and valid < '%s'
          and t.network ~* 'RWIS' and t.iemid = c.iemid""" % (
        ts,
        ts2,
    )
    icursor.execute(sql)
    rows = icursor.fetchall()
    if not rows:
        print("No RWIS obs found between %s and %s" % (ts, ts2))
    icursor.close()

    # Write to RWIS Archive
    rcursor = rwisdb.cursor()
    rcursor.executemany(
        f"""INSERT into t{ts.year} (station, valid, tmpf,
        dwpf, drct, sknt, tfs0, tfs1, tfs2, tfs3, subf, gust, tfs0_text,
        tfs1_text, tfs2_text, tfs3_text, pcpn, vsby) VALUES (%(station)s,
        %(valid)s,%(tmpf)s,%(dwpf)s,%(drct)s,%(sknt)s,%(tsf0)s,
        %(tsf1)s,%(tsf2)s,%(tsf3)s,%(rwis_subf)s,%(gust)s,%(scond0)s,
        %(scond1)s,%(scond2)s,%(scond3)s,%(pday)s,%(vsby)s)""",
        rows,
    )
    rcursor.close()

    rwisdb.commit()
    iemdb.commit()
    rwisdb.close()
    iemdb.close()


if __name__ == "__main__":
    main(sys.argv)
