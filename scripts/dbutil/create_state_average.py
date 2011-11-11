import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
POSTGIS = iemdb.connect('postgis')
pcursor = POSTGIS.cursor()

# Get the sites
pcursor.execute("""select state_abbr, state_name, x(ST_Centroid(the_geom)), 
  y(ST_Centroid(the_geom)) from states where 
  state_abbr in ('MN','WI','MI','OH','IL','IN','MO','KS','NE','ND','SD','KY')""")
for row in pcursor:
  data = {}
  if row[1] is None:
    continue
  data['state'] = row[0]
  data['id'] = "%s0000" % (row[0],)
  data['lon'] = row[2]
  data['lat'] = row[3]
  data['name'] = "%s Average" % (row[1],)
  # See if the site exists
  mcursor.execute("SELECT * from stations where id = %s", (data['id'],))
  if mcursor.rowcount != 0:
    print data['id']
    continue

  sql = """INSERT into stations(id, synop, name, state, country, network, online,
         geom, plot_name 
         ) VALUES ('%(id)s', 99999, '%(name)s', '%(state)s', 'US', 
  '%(state)sCLIMATE', 't', 'SRID=4326;POINT(%(lon)s %(lat)s)',  '%(name)s')""" % data
  mcursor.execute(sql)

MESOSITE.commit()
mcursor.close()

