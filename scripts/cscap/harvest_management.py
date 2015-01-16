'''
 Harvest the data in the data management store!
'''
import util
import ConfigParser
import psycopg2
import sys

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

spread = util.Spreadsheet(docs_client, spr_client, 
                          config.get('cscap', 'manstore'))

translate = {'date': 'valid'}


for sheetkey in ['Operations', 'Management', 'Pesticides']:
    current = {}
    if sheetkey == 'Operations':
        pcursor.execute("""SELECT valid, uniqueid, updated, operation, cropyear 
        from operations""")
    elif sheetkey == 'Management':
        pcursor.execute("""SELECT '', uniqueid,    updated, '',       cropyear
        from management""")
    else:
        pcursor.execute("""SELECT valid, uniqueid, updated, crop, cropyear
        from pesticides""")
    for row in pcursor:
        v = row[0]
        if v is not None and type(v) != type(''):
            v = v.strftime("%-m/%-d/%Y")
        key = "%s,%s,%s,%s,%s" % (v, row[1], row[2], row[3], row[4])
        current[key] = True
    sheet = spread.worksheets[sheetkey]
    
    added = 0
    dups = 0
    for entry in sheet.get_list_feed().entry:
        d = entry.to_dict()
        key = '%s,%s,%s,%s,%s' % (d.get('date', ''), d.get('uniqueid'),
                                  d.get('updated'), 
            d.get('operation' if sheetkey == 'Operations' else 'crop', ''),
            d.get('cropyear'))
        if current.has_key(key):
            dups += 1
            continue
        cols = []
        vals = []
        for key in d.keys():
            vals.append( d[key] )
            cols.append( translate.get(key,key) )
            
        sql = """INSERT into %s(%s) VALUES (%s)""" % (sheetkey, ",".join(cols),
                                                        ','.join(["%s"]*len(cols)))
        pcursor.execute(sql, vals)
        added += 1
        
    print "   harvest_management %s %4s dups %4s added" % (sheetkey, dups,
                                                             added)
pcursor.close()
pgconn.commit()
pgconn.close()