import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
POSTGIS = iemdb.connect('postgis')
pcursor = POSTGIS.cursor()

# Get the sites
pcursor.execute("""select name, st, stdiv_, x(ST_Centroid(ST_Transform(the_geom,4326))), y(ST_Centroid(ST_Transform(the_geom,4326))) , ST_Area(the_geom) as area from climate_div ORDER by area ASC""")
for row in pcursor:
  data = {}
  if row[1] is None:
    continue
  data['state'] = row[1]
  data['id'] = "%s%02i" % (row[1], int(str(row[2])[4:]))
  data['lon'] = row[3]
  data['lat'] = row[4]
  data['name'] = row[0]
  # See if the site exists
  #mcursor.execute("SELECT * from stations where id = %s", (data['id'],))
  #if mcursor.rowcount != 0:
  #  print data['id']
  #  continue

  #sql = """INSERT into stations(id, synop, name, state, country, network, online,
  #       geom, plot_name 
  #       ) VALUES ('%(id)s', 99999, '%(name)s', '%(state)s', 'US', 
  #'_CLIMDIV', 't', 'SRID=4326;POINT(%(lon)s %(lat)s)',  '%(name)s')""" % data
  sql = """UPDATE stations SET geom = 'SRID=4326;POINT(%(lon)s %(lat)s)' 
 WHERE id = '%(id)s' and network = '_CLIMDIV'""" % data
  print sql
  mcursor.execute(sql)

mcursor.close()
MESOSITE.commit()

