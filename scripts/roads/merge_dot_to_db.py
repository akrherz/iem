''' 
Take the raw shapefile kindly provided by the DOT and merge it to my
antiquated schema


 id       | numeric                         | 
 route    | character varying(5)            | 
 nameid   | character varying(72)           | 
 longname | character varying(165)          | 
 geom     | geometry(MultiLineString,26915) | 

 segid       | integer                | <-- default
 major       | character varying(10)  | direct from route
 minor       | character varying(128) | nameid past first : and strip
 us1         | smallint               | conditional
 st1         | smallint               | conditional
 int1        | smallint               | conditional
 type        | smallint               | 1, 2, or 3
 wfo         | character(3)           | filled in later
 tempval     | numeric                | 
 geom        | geometry               | direct copy
 simple_geom | geometry               | ST_Simplify


'''
import psycopg2
conn = psycopg2.connect(database='postgis')
conn2 = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = conn.cursor()
cursor2 = conn2.cursor()

cursor.execute("""
 SELECT route, nameid, longname, geom from roads_new
 """)
for row in cursor:
    route = row[0]
    nameid = row[1]
    longname = row[2]
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
        st1 = int( route.replace("US", ""))
    elif route.find("IA") == 0:
        code = 3
        st1 = int( route.replace("IA", ""))
    else:
        print route
    
    minor = nameid.split(":")[1].strip()
    
    cursor2.execute("""
    INSERT into roads_base(major, minor, us1, st1, int1, type, geom, longname) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (route, minor, us1, st1, int1, code, geom, longname))

cursor2.close()
conn2.commit()
conn2.close()