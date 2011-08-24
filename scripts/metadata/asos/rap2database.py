import sys, iemdb, os
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()

country = sys.argv[1]

for line in open('stations.txt'):
  if len(line) < 70:
    continue
  if line[81:83] == country:
    data = {}
    data['id'] = line[20:24]
    if data['id'][0] == 'K':
      data['id'] = data['id'][1:]
    #data['state'] = line[:2]
    #data['state'] = country
    data['state'] = sys.argv[2]
    data['name'] = line[3:19].replace("'", "")
    data['lat'] = float(line[39:41]) + (float(line[42:44])/60.0)
    if line[44] == 'S':
      data['lat'] = 0 - data['lat']

    data['lon'] = float(line[47:50]) + (float(line[51:53])/60.0)
    if line[53] == 'W':
      data['lon'] = 0 - data['lon']
    data['elev'] = float(line[55:59])
    

    sql = """INSERT into stations(id, synop, name, state, country, 
         network, online, geom, plot_name, elevation
         ) VALUES ('%(id)s', 99999, '%(name)s', '%(state)s', '%(state)s', 
         '%(state)s_ASOS', 't', 'SRID=4326;POINT(%(lon)s %(lat)s)',  
         '%(name)s', %(elev)s)""" % data

    mcursor = MESOSITE.cursor()
    try:
      mcursor.execute(sql)
    except:
      mcursor.close()
    MESOSITE.commit()


    cmd = "/mesonet/python/bin/python /mesonet/www/apps/iemwebsite/scripts/util/addSiteMesosite.py %s_ASOS %s" % (data['state'], data['id'])
    os.system(cmd)

MESOSITE.close()
