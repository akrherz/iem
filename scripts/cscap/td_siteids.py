import pyiem.cscap_utils as util
import psycopg2

pgconn = psycopg2.connect(database='mesosite', host='iemdb', port=5555,
                          user='mesonet')
cursor = pgconn.cursor()

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)

spreadsheet = util.Spreadsheet(spr_client,
                               '1oZ2NEmoa0XHSGTWKaBLt0DJK1kIbpWO6iSZ0I2OE2gA')
spreadsheet.get_worksheets()

lf = spreadsheet.worksheets['Research Site Metadata'].get_list_feed()
for entry in lf.entry:
    data = entry.to_dict()
    siteid = data['uniqueid'].strip()
    name = ('%s [%s]' % (data['farmfieldname'][:(61-len(data['leadpi']))],
                         data['leadpi'])).replace("\n", " ")
    if data['latitudedd.d'] == 'TBD':
        print 'Skipping %s due to TBD location' % (name,)
        continue
    cursor.execute("""SELECT climate_site from stations where id = %s
    and network = 'TD'
    """, (siteid,))
    if cursor.rowcount == 0:
        cursor.execute("""INSERT into stations (id, name, state, country,
    network, online, geom, metasite) VALUES (%s, %s, %s, 'US',
    'TD', 'f', %s, 't')""", (siteid, name, data['state'],
                             'SRID=4326;POINT(%s %s)' % (
                                                    data['longitudeddd.d'],
                                                    data['latitudedd.d'])))
    else:
        cursor.execute("""UPDATE stations SET name = %s
        WHERE id = %s and network = 'TD' RETURNING climate_site
        """, (name, siteid))
        climatesite = cursor.fetchone()[0]
        if (climatesite is not None and climatesite != '' and
                climatesite != data['iemclimatesite']):
            entry.set_value('iemclimatesite', climatesite)
            print 'Setting climate site: %s for site: %s' % (climatesite,
                                                             siteid)
            util.exponential_backoff(spr_client.update, entry)

cursor.close()
pgconn.commit()
pgconn.close()
