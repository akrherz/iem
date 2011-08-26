import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
POSTGIS = iemdb.connect('postgis')
pcursor = POSTGIS.cursor()

# Get the sites
pcursor.execute("""select name, st, stdiv_, x(ST_Centroid(the_geom)), y(ST_Centroid(the_geom)) , ST_Area(the_geom) as area from climate_div ORDER by area DESC""")
for row in pcursor:
  data = {}
  if row[1] is None:
    continue
  data['state'] = row[1]
  data['id'] = "%s%s" % (row[1], str(row[2])[4:])
  data['lon'] = row[3]
  data['lat'] = row[4]
  data['name'] = row[0]
  # See if the site exists
  mcursor.execute("SELECT * from stations where id = %s", (data['id'],))
  if mcursor.rowcount != 0:
    print data['id']
    continue

  sql = """INSERT into stations(id, synop, name, state, country, network, online,
         geom, plot_name 
         ) VALUES ('%(id)s', 99999, '%(name)s', '%(state)s', 'US', 
  '_CLIMDIV', 't', 'SRID=4326;POINT(%(lon)s %(lat)s)',  '%(name)s')""" % data
  mcursor.execute(sql)

MESOSITE.commit()
mcursor.close()

