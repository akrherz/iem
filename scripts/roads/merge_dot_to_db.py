"""Importing IDOT provided Road Conditions

Fall 2016 notes

 shp2pgsql -s 3857 SEGMENTS_WGS84_SPHERICAL.shp new_roads | psql postgis


update new_roads SEt nameid = replace(nameid, 'I-35/80', 'I-80'),
 route_name = 'I-80'  where route_name ~* '/';

1031 rows entered

 gid        | integer                        |
 segment_id | numeric(10,0)                  |
 route      | character varying(80)          |
 nameid     | character varying(80)          |
 longname   | character varying(156)         |
 district   | character varying(80)          |
 subarea    | character varying(80)          |
 primarymp  | numeric                        |
 primarylat | numeric                        |
 primarylon | numeric                        |
 secondarym | numeric                        |
 secondaryl | numeric                        |
 secondar_1 | numeric                        |
 event_id   | character varying(80)          |
 event_upda | numeric(10,0)                  |
 hl_pavemen | character varying(80)          |
 loc_link_d | character varying(80)          |
 road_condi | character varying(80)          |
 cars_msg_u | date                           |
 cars_msg_i | date                           |
 ph_pavemen | character varying(80)          |
 shape_leng | numeric                        |
 district_n | numeric(10,0)                  |
 cost_cente | character varying(80)          |
 editor     | character varying(80)          |
 edited_dat | date                           |
 condition_ | date                           |
 conditio_1 | date                           |
 conditio_2 | numeric                        |
 route_name | character varying(80)          |
 geom       | geometry(MultiLineString,3857) |



roads base is

 segid       | integer                         | This is autoset
 major       | character varying(10)           | directly use route
 minor       | character varying(128)          | split nameid by :, take 2
 us1         | smallint                        | logic on route
 st1         | smallint                        | logic on route
 int1        | smallint                        | logic on route
 type        | smallint                        | logic on route
 wfo         | character(3)                    | assign later with spatial Q
 longname    | character varying(256)          | directly use longname
 geom        | geometry(MultiLineString,26915) | directly use geom
 simple_geom | geometry(MultiLineString,26915) | compute via Spatial Q
 idot_id       | integer                         | use segment_id
 archive_begin | timestamp with time zone        | unset
 archive_end   | timestamp with time zone        | unset


"""
import sys

from pyiem.util import get_dbconn

conn = get_dbconn("postgis", host="localhost")
conn2 = get_dbconn("postgis", user="mesonet")
cursor = conn.cursor()
cursor2 = conn2.cursor()

cursor2.execute("""DELETE from roads_current""")

cursor.execute(
    """
     SELECT route_name, nameid, longname, ST_Transform(geom, 26915), segment_id
     from new_roads
"""
)
for row in cursor:
    (route, name_id, longname, geom, gid) = row
    major = route
    minor = name_id.split(":")[1]
    (typ, num) = route.replace("-", " ").split()
    int1 = num if typ == "I" else None
    us1 = num if typ == "US" else None
    st1 = num if typ == "IA" else None
    if typ not in ["I", "US", "IA"]:
        print("Totally unknown, abort %s" % (route,))
        sys.exit()
    sys_id = 1
    if typ == "US":
        sys_id = 2
    elif typ == "IA":
        sys_id = 3
    idot_id = gid

    # OK, insert this into the database!
    cursor2.execute(
        """
    INSERT into roads_base(major, minor, us1, st1, int1, type, geom, longname,
    idot_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING segid
    """,
        (major, minor, us1, st1, int1, sys_id, geom, longname, idot_id),
    )
    segid = cursor2.fetchone()[0]
    # Create the simplified geom
    cursor2.execute(
        """UPDATE roads_base
    SET simple_geom = ST_Simplify(geom, 0.01) WHERE segid = %s""",
        (segid,),
    )

    # Figure out which WFO this segment is in...
    cursor2.execute(
        """SELECT u.wfo,
    ST_Distance(u.geom, ST_Transform(b.geom, 4326))
    from ugcs u, roads_base b WHERE
    substr(ugc, 1, 2) = 'IA' and b.segid = %s
    and u.end_ts is null ORDER by ST_Distance ASC""",
        (segid,),
    )
    wfo = cursor2.fetchone()[0]
    print('Added [%s] "%s" segid:%s wfo:%s' % (longname, name_id, segid, wfo))
    cursor2.execute(
        """UPDATE roads_base SET wfo = %s WHERE segid = %s
    """,
        (wfo, segid),
    )

    # Add a roads_current entry!
    cursor2.execute(
        """INSERT into roads_current(segid, valid)
     VALUES (%s, now())"""
        % (segid,)
    )


cursor2.close()
conn.commit()
conn.close()
conn2.commit()
conn2.close()
