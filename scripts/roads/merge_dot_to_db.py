"""Importing IDOT provided Road Conditions

shp2pgsql -s 26915 ROAD_COND_SEGMENTS_STAGE.shp new_roads | psql postgis

1049 rows entered

 gid        | integer                         |
 segment_id | numeric(10,0)                   |
 route_name | character varying(10)           |
 name_id    | character varying(100)          |
 primary_la | numeric                         |
 primary_lo | numeric                         |
 secondary_ | numeric                         |
 secondary1 | numeric                         |
 segment_st | date                            |
 segment_en | date                            |
 primary_mp | numeric                         |
 secondary2 | numeric                         |
 id         | numeric                         |
 long_name  | character varying(165)          |
 area       | character varying(50)           |
 sub_area   | character varying(50)           |
 lrs_rte_id | character varying(20)           |
 sys_id     | numeric                         |
 rte_num    | numeric                         |
 geom       | geometry(MultiLineString,26915) |

roads base is

 segid       | integer                         | This is autoset
 major       | character varying(10)           | directly use route_name
 minor       | character varying(128)          | split name_id by :, take 2
 us1         | smallint                        | sys_id == 2, take rte_num
 st1         | smallint                        | sys_id == 3, take rte_num
 int1        | smallint                        | sys_id == 1, take rte_num
 type        | smallint                        | directly use sys_id
 wfo         | character(3)                    | assign later with spatial Q
 tempval     | numeric                         | unused?  will drop?
 longname    | character varying(256)          | directly use long_name
 geom        | geometry(MultiLineString,26915) | directly use geom
 simple_geom | geometry(MultiLineString,26915) | compute via Spatial Q


"""
import psycopg2
conn = psycopg2.connect(database='postgis', host='iemdb')
cursor = conn.cursor()
cursor2 = conn.cursor()

cursor.execute("""
     SELECT route_name, name_id, sys_id, rte_num, long_name, geom
     from new_roads
""")
for row in cursor:
    (route_name, name_id, sys_id, rte_num, long_name, geom) = row

    int1 = rte_num if sys_id == 1 else None
    us1 = rte_num if sys_id == 2 else None
    st1 = rte_num if sys_id == 3 else None
    # OK, insert this into the database!
    cursor2.execute("""
    INSERT into roads_base(major, minor, us1, st1, int1, type, geom, longname)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING segid
    """, (route_name.strip(),
          name_id.split(":")[1].strip(),
          us1, st1, int1,
          sys_id, geom, long_name))
    segid = cursor2.fetchone()[0]
    # Create the simplified geom
    cursor2.execute("""UPDATE roads_base
    SET simple_geom = ST_Simplify(geom, 0.01) WHERE segid = %s""", (segid,))

    # Figure out which WFO this segment is in...
    cursor2.execute("""SELECT u.wfo,
    ST_Distance(u.geom, ST_Transform(b.geom, 4326))
    from ugcs u, roads_base b WHERE
    substr(ugc, 1, 2) = 'IA' and b.segid = %s
    and u.end_ts is null ORDER by ST_Distance ASC""", (segid,))
    wfo = cursor2.fetchone()[0]
    print('Added [%s] "%s" segid:%s wfo:%s' % (route_name, name_id, segid,
                                               wfo))
    cursor2.execute("""UPDATE roads_base SET wfo = %s WHERE segid = %s
    """, (wfo, segid))

    # Add a roads_current entry!
    cursor2.execute("""INSERT into roads_current(segid, valid)
     VALUES (%s, now())""" % (segid, ))


cursor2.close()
conn.commit()
conn.close()
