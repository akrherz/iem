# Process Traffic Data
import csv, psycopg2
import psycopg2.extras

DBCONN = psycopg2.connect(database="iem", host="iemdb")
#DBCONN = psycopg2.connect(database="iem")

def load_metadata():
    """
    Load up what we know about these traffic sites
    """
    meta = {}
    cur = DBCONN.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT * from rwis_traffic_meta""")
    rows = cur.fetchall()
    cur.close()
    for row in rows:
        key = "%s_%s" % (row["location_id"], row["lane_id"])
        meta[ key ] = row["sensor_id"]
    return meta

def create_sensor( row ):
    """
    Create a sensor in the database please
    """
    print "Adding RWIS Traffic Sensor: %s Lane: %s Name: %s" % (
      row["site_id"], row["Lane_id"], row["Sensor_position_name"])
    cursor = DBCONN.cursor()
    cursor.execute("""INSERT into rwis_traffic_sensors(location_id,
     lane_id, name) VALUES (%s, %s, %s)""", (row["site_id"],
     row["Lane_id"], row["Sensor_position_name"]))
    cursor.close()

def create_traffic( key ):
    """
    Need to initialize the rwis_traffic_data table
    """
    cursor = DBCONN.cursor()
    cursor.execute("""INSERT into rwis_traffic_data(sensor_id)
     VALUES (%s)""", (key,))
    cursor.close()

def processfile( fp ):
    meta = load_metadata()
    o = open("/mesonet/data/incoming/rwis/%s" % (fp,), 'r')
    data = []
    for row in csv.DictReader( o ):
      key = "%s_%s" % (int(row["site_id"]), int(row["Lane_id"]))
      if not meta.has_key(key):
         create_sensor( row )
         meta = load_metadata()
         create_traffic( meta[key] )
      row["sensor_id"] = meta[key]
      if row["long_vol"] == "":
        row["long_vol"] = None
      if row["occupancy"] == "":
        row["occupancy"] = None
      if row["normal_vol"] == "":
        row["normal_vol"] = None
      if row["avg_speed"] == "":
        row["avg_speed"] = None
      data.append( row )
    o.close()

    cursor = DBCONN.cursor()
    cursor.execute("SET TIME ZONE 'GMT'")
    cursor.executemany("""UPDATE rwis_traffic_data SET 
      valid = %(obs_date_time)s, avg_speed = %(avg_speed)s,
      avg_headway = %(avg_headway)s, normal_vol = %(normal_vol)s,
      long_vol = %(long_vol)s,  occupancy = %(occupancy)s
      WHERE sensor_id = %(sensor_id)s""", data)
    cursor.close()
    DBCONN.commit()
    DBCONN.close()

if __name__ == '__main__':
    processfile("TrafficFile.csv")
