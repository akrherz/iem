"""Get the Plot IDs harvested!"""
import util
import sys
import ConfigParser
import psycopg2

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient()

res = drive_client.files().list(
        q="title contains 'Plot Identifiers'").execute()

translate = {'column': 'col'}

lookup = {'tillage': 'TIL',
          'rotation': 'ROT',
          'drainage': 'DWM',
          'nitrogen': 'NIT',
          'landscape': 'LND'}

pcursor.execute("""DELETE from plotids""")
removed = pcursor.rowcount
added = 0
for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    worksheet = spreadsheet.worksheets['Sheet 1']
    for entry2 in worksheet.get_list_feed().entry:
        d = entry2.to_dict()
        cols = []
        vals = []
        for key in d.keys():
            v = None
            if d[key] is None:
                continue
            if d[key] is not None:
                v = d[key].strip().replace("[", "").replace("]", "").split()[0]
                v = "%s%s" % (lookup.get(key, ''), v)
            if key == 'uniqueid':
                v = v.upper()
            if key.startswith('no3') or key.startswith('_'):
                continue
            vals.append(v)
            cols.append(translate.get(key, key))
        if len(cols) == 0:
            continue
        sql = """
            INSERT into plotids(%s) VALUES (%s)
        """ % (",".join(cols), ','.join(["%s"]*len(cols)))
        try:
            pcursor.execute(sql, vals)
        except Exception, exp:
            print exp
            print item['title']
            print cols
            sys.exit()
        added += 1

if removed > (added + 10):
    print 'Aborting harvest_plotids due to sz'
    sys.exit()
print "   harvest_plotids %s removed, %s added" % (removed, added)
pcursor.close()
pgconn.commit()
pgconn.close()
