"""Importing IDOT provided Road Conditions

shp2pgsql -s 26915 ROAD_COND_SEGMENTS_STAGE.shp new_roads | psql postgis

1052 rows entered

                                        Table "public.new_roads"
   Column   |              Type               |       Modifiers
------------+---------------------------------+----------------------
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
 geom       | geometry(MultiLineString,26915) |

"""
import psycopg2
conn = psycopg2.connect(database='postgis')
conn2 = psycopg2.connect(database='postgis', host='localhost', port='5555',
                         user='mesonet')
cursor = conn.cursor()
cursor2 = conn2.cursor()

MISSING = """
I-29 between Exit 95: County Road F20 (near Little Sioux) and Exit 112: IA 175 (near Onawa)
I-29 between Exit 112: IA 175 (near Onawa) and Exit 127: IA 141; County Road K42 (near Sloan)
I-29 between Exit 127: IA 141; County Road K42 (near Sloan) and Exit 141: 1st Street and Sioux Gateway Airport (Sergeant Bluff)
I-80 between Exit 142: US 6; US 65; Hubbell Avenue (Altoona) and Exit 149: County Road S27 (near Mitchellville)
I-80 between Exit 254: County Road X30 and Exit 265: County Road X46 (8 miles east of the West Branch area)
I-80 between Exit 265: County Road X46 (8 miles east of the West Branch area) and Exit 271: US 6; IA 38 and County Road X64 (5 miles west of the Durant area)
I-80 between Exit 271: US 6; IA 38 and County Road X64 (5 miles west of the Durant area) and Exit 290: I-280; US 6 (1 mile east of the Walcott area)
US 6 between IA 14 (near Newton) and IA 224 (near Kellogg)
US 20 between County Road X47 (near Dyersville) and Exit 308: County Road Y21 (near Centralia)
US 30 between County Road X40 (near Mechanicsville) and County Road Y14 (near Clarence)
US 30 between IA 38 (near Clarence) and County Road Y4E (near Wheatland)
US 151 between IA 136 (near Cascade) and US 61 (near Dubuque)
IA 28 between IA 92 (Martensdale) and IA 5 (near Norwalk)
IA 37 between IA 175 (near Turin) and US 30 (Dunlap)
IA 37 between US 30 (Dunlap) and IA 191 (Earling)
IA 44 between US 169 (near Dallas Center) and IA 141 (near Grimes)
IA 141 between IA 175 (Mapleton) and County Road L61 (near Charter Oak)
IA 141 between I-29; County Road K42 (near Sloan) and IA 31 (Rodney)
IA 163 between I-235 (near Des Moines) and IA 117 (3 miles west of the Prairie City area)
IA 163 between IA 117 (Prairie City) and IA 14 (Monroe)
IA 175 between Burt County the Missouri River bridge (5 miles west of the Onawa area) and IA 37 (near Turin)
IA 183 between IA 127 (near Pisgah) and IA 141 (Ute)
"""
miss = []
for line in MISSING.split("\n"):
    if line.strip() != '':
        miss.append(line.strip())
print len(miss)
cursor.execute("""
 SELECT route_name, name_id, long_name, geom from new_roads WHERE
 long_name is not null
 """)
for row in cursor:
    route = row[0]
    nameid = row[1]
    longname = row[2].replace(", between", " between")
    if longname not in miss:
        continue
    miss.remove(longname)
    geom = row[3]
    # Processing!
    code = None
    int1 = None
    st1 = None
    us1 = None
    if route.find("I-") == 0:
        code = 1
        int1 = int( route.replace("I-", ""))
    elif route.find("US") == 0:
        code = 2
        us1 = int( route.replace("US", ""))
    elif route.find("IA") == 0:
        code = 3
        st1 = int( route.replace("IA", ""))
    else:
        print route
    
    minor = nameid.split(":")[1].strip()
    cursor2.execute("""
    INSERT into roads_base(major, minor, us1, st1, int1, type, geom, longname) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING segid
    """, (route, minor, us1, st1, int1, code, geom, longname))
    segid = cursor2.fetchone()[0]
    print 'Added %s' % (segid, )
    cursor2.execute("""UPDATE roads_base SET simple_geom = ST_Simplify(geom, 0.01)
    WHERE segid = %s""", (segid,))
    cursor2.execute("""INSERT into roads_current(segid, valid)
     VALUES (%s, now())""" % (segid, )) 

print len(miss)
print miss

cursor2.close()
conn2.commit()
conn2.close()
