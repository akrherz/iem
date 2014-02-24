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

for sheetkey in ['Management', 'Pesticides', 'Operations']:
    sheet = spread.worksheets[sheetkey]
    
    pcursor.execute("""DELETE from %s """ % (sheetkey,))
    removed = pcursor.rowcount
    added = 0
    for entry in sheet.get_list_feed().entry:
        d = entry.to_dict()
        cols = []
        vals = []
        for key in d.keys():
            vals.append( d[key] )
            cols.append( translate.get(key,key) )
        sql = """INSERT into %s(%s) VALUES (%s)""" % (sheetkey, ",".join(cols),
                                                        ','.join(["%s"]*len(cols)))
        pcursor.execute(sql, vals)
        added += 1
        
    if removed > (added + 10):
        print 'Aborting harvest_management due to sz'
        sys.exit()
    print "   harvest_management %s %s removed, %s added" % (sheetkey, removed,
                                                             added)
pcursor.close()
pgconn.commit()
pgconn.close()