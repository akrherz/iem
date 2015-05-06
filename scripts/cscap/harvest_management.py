'''
 Harvest the data in the data management store!
'''
import util
import ConfigParser
import psycopg2

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn', user='mesonet',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)

spread = util.Spreadsheet(spr_client,
                          config.get('cscap', 'manstore'))

translate = {'date': 'valid'}


for sheetkey in ['Operations', 'Management', 'Pesticides']:
    current = {}
    found = {}
    if sheetkey == 'Operations':
        pcursor.execute("""
            SELECT valid, uniqueid, updated, operation, cropyear, oid
            from operations
        """)
    elif sheetkey == 'Management':
        pcursor.execute("""
            SELECT '', uniqueid,    updated, '',       cropyear, oid
            from management
        """)
    else:
        pcursor.execute("""
            SELECT valid, uniqueid, updated, crop, cropyear, oid
            from pesticides
        """)
    for row in pcursor:
        v = row[0]
        if v is not None and not isinstance(v, str):
            v = v.strftime("%-m/%-d/%Y")
        key = "%s,%s,%s,%s,%s" % (v, row[1], row[2], row[3], row[4])
        current[key] = row[5]
    sheet = spread.worksheets[sheetkey]

    added = 0
    dups = 0
    entries = 0
    for entry in sheet.get_list_feed().entry:
        entries += 1
        d = entry.to_dict()
        # Units row has n/a as the date, so skip it
        if d.get('date') == 'n/a':
            continue
        key = ('%s,%s,%s,%s,%s'
               ) % (d.get('date', ''), d.get('uniqueid'), d.get('updated'),
                    d.get('operation' if sheetkey == 'Operations' else 'crop',
                          ''), d.get('cropyear'))
        if key in current:
            del(current[key])
            found[key] = True
            dups += 1
            continue
        if key in found:
            print 'DUP: ', key
            continue
        cols = []
        vals = []
        for key in d.keys():
            vals.append(d[key])
            cols.append(translate.get(key, key))

        sql = """
            INSERT into %s(%s) VALUES (%s)
            """ % (sheetkey, ",".join(cols), ','.join(["%s"]*len(cols)))
        pcursor.execute(sql, vals)
        added += 1

    for key in current.keys():
        pcursor.execute("""DELETE from """+sheetkey+""" WHERE oid = %s""",
                        (current[key],))

    print "   harvest_management %s %4s rows %4s dups %4s add %4s del" % (
        sheetkey, entries, dups, added, len(current))

pcursor.close()
pgconn.commit()
pgconn.close()
