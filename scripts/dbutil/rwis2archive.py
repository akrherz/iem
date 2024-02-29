"""
Copy RWIS data from iem database to its final resting home in 'rwis'

called from RUN_10_AFTER.sh
"""

import datetime
import sys

from pyiem.reference import ISO8601
from pyiem.util import get_dbconnc, get_properties, logger, set_property, utc

LOG = logger()
PROPERTY_NAME = "rwis2archive_last"


def get_first_updated():
    """Figure out which is the last updated timestamp we ran for."""
    props = get_properties()
    propvalue = props.get(PROPERTY_NAME)
    if propvalue is None:
        LOG.warning("iem property %s is not set, abort!", PROPERTY_NAME)
        sys.exit()

    dt = datetime.datetime.strptime(propvalue, ISO8601)
    return dt.replace(tzinfo=datetime.timezone.utc)


def process_traffic(first_updated, last_updated):
    """Process what traffic has."""
    ipgconn, icursor = get_dbconnc("iem")
    rpgconn, rcursor = get_dbconnc("rwis")
    icursor.execute(
        """SELECT l.nwsli as station, s.lane_id::int as lane_id, d.* from
       rwis_traffic_data_log d, rwis_locations l, rwis_traffic_sensors s
       WHERE s.id = d.sensor_id and updated >= %s and updated < %s
       and s.location_id = l.id""",
        (first_updated, last_updated),
    )
    deleted = 0
    inserts = 0
    for row in icursor:
        rcursor.execute(
            "delete from alldata_traffic where station = %s and valid = %s",
            (row["station"], row["valid"]),
        )
        deleted += rcursor.rowcount
        rcursor.execute(
            """INSERT into alldata_traffic (station, valid,
            lane_id, avg_speed, avg_headway, normal_vol, long_vol, occupancy)
            VALUES (%(station)s,%(valid)s,
            %(lane_id)s, %(avg_speed)s, %(avg_headway)s, %(normal_vol)s,
            %(long_vol)s, %(occupancy)s)
            """,
            row,
        )
        inserts += 1
    icursor.execute(
        "delete from rwis_traffic_data_log where "
        "updated >= %s and updated < %s",
        (first_updated, last_updated),
    )
    rcursor.close()
    rpgconn.commit()
    rpgconn.close()
    icursor.close()
    ipgconn.commit()
    ipgconn.close()
    LOG.info("access: %s rows, rwis: %s dels", inserts, deleted)


def process_soil(first_updated, last_updated):
    """Do the soil work."""
    ipgconn, icursor = get_dbconnc("iem")
    rpgconn, rcursor = get_dbconnc("rwis")

    icursor.execute(
        """SELECT l.nwsli as station, d.valid,
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
         WHERE updated >= %s and updated < %s and d.location_id = l.id
         GROUP by station, valid""",
        (first_updated, last_updated),
    )
    deleted = 0
    inserts = 0
    for row in icursor:
        rcursor.execute(
            "delete from alldata_soil where station = %s and valid = %s",
            (row["station"], row["valid"]),
        )
        deleted += rcursor.rowcount
        rcursor.execute(
            """INSERT into alldata_soil
            (station, valid,
            tmpf_1in, tmpf_3in, tmpf_6in, tmpf_9in, tmpf_12in, tmpf_18in,
            tmpf_24in, tmpf_30in, tmpf_36in, tmpf_42in, tmpf_48in, tmpf_54in,
            tmpf_60in, tmpf_66in, tmpf_72in) VALUES (
            %(station)s,%(valid)s,
            %(tmpf_1in)s, %(tmpf_3in)s, %(tmpf_6in)s, %(tmpf_9in)s,
            %(tmpf_12in)s,
            %(tmpf_18in)s, %(tmpf_24in)s, %(tmpf_30in)s, %(tmpf_36in)s,
            %(tmpf_42in)s, %(tmpf_48in)s, %(tmpf_54in)s, %(tmpf_60in)s,
            %(tmpf_66in)s, %(tmpf_72in)s)
            """,
            row,
        )
        inserts += 1
    icursor.execute(
        "delete from rwis_soil_data_log where "
        "updated >= %s and updated < %s",
        (first_updated, last_updated),
    )
    rcursor.close()
    rpgconn.commit()
    rpgconn.close()
    icursor.close()
    ipgconn.commit()
    ipgconn.close()
    LOG.info("access: %s rows, rwis: %s dels", inserts, deleted)


def process_obs(first_updated, last_updated):
    """Take obs."""
    ipgconn, icursor = get_dbconnc("iem")
    rpgconn, rcursor = get_dbconnc("rwis")

    icursor.execute(
        """
        SELECT c.*, t.id as station from current_log c, stations t
        WHERE updated >= %s and updated < %s
          and t.network ~* 'RWIS' and t.iemid = c.iemid
                    """,
        (first_updated, last_updated),
    )
    deleted = 0
    for row in icursor:
        rcursor.execute(
            "delete from alldata where station = %s and valid = %s",
            (row["station"], row["valid"]),
        )
        deleted += rcursor.rowcount
        rcursor.execute(
            """INSERT into alldata (station, valid, tmpf,
            dwpf, drct, sknt, tfs0, tfs1, tfs2, tfs3, subf, gust, tfs0_text,
            tfs1_text, tfs2_text, tfs3_text, pcpn, vsby) VALUES (%(station)s,
            %(valid)s,%(tmpf)s,%(dwpf)s,round(%(drct)s::numeric, 0),%(sknt)s,
            %(tsf0)s,%(tsf1)s,%(tsf2)s,%(tsf3)s,%(rwis_subf)s,%(gust)s,
            %(scond0)s,
            %(scond1)s,%(scond2)s,%(scond3)s,%(pday)s,%(vsby)s)""",
            row,
        )
    rcursor.close()
    rpgconn.commit()
    rpgconn.close()
    ipgconn.close()
    LOG.info("access: %s rows, rwis: %s dels", icursor.rowcount, deleted)


def main():
    """Go main"""
    last_updated = utc()
    first_updated = get_first_updated()

    process_traffic(first_updated, last_updated)
    process_soil(first_updated, last_updated)
    process_obs(first_updated, last_updated)

    set_property(PROPERTY_NAME, last_updated)


if __name__ == "__main__":
    main()
