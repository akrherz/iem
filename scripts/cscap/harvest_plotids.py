"""Get the Plot IDs harvested!"""
import pyiem.cscap_utils as util
import sys
import psycopg2

config = util.get_config()

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config['database']['host'])
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient(config)

res = drive_client.files().list(
        q="title contains 'Plot Identifiers'").execute()

translate = {'column': 'col'}

lookup = {'tillage': 'TIL',
          'rotation': 'ROT',
          'herbicide': 'HERB',
          'drainage': 'DWM',
          'nitrogen': 'NIT',
          'landscape': 'LND'}

pcursor.execute("""DELETE from plotids""")
removed = pcursor.rowcount
added = 0
sheets = 0
for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    sheets += 1
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
                if v != 'N/A':
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

print(("harvest_plotids, removed: %s, added: %s, sheets: %s"
       ) % (removed, added, sheets))
if removed > (added + 10):
    print("harvest_plotids, aborting due to large difference")
    sys.exit()
pcursor.close()
pgconn.commit()
pgconn.close()
