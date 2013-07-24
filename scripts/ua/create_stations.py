
for line in open('raob.short'):
    if line[0] == '(' or line[:4] == 'Name':
        continue
    sid = line[:4].strip()
    if sid[0] == 'C' or len(sid) == 3:
        wmo = line[5:10]
        lat = float( line[13:18])
        lon = float( line[19:25])
        name = line[32:].strip()
        country = 'US'
        if len(sid) == 4:
            country = 'CA'
            
        sql = """INSERT into stations(synop, name, country, network, online,
        geom, plot_name, id, metasite) values (%s, '%s', '%s', 'RAOB', 't',
        'SRID=4326;POINT(%s %s)', '%s', '%s', 't');""" % (wmo, name, country,
                                                         lon, lat, name, sid)
        print sql