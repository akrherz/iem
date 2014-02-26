'''
 Get the Plot IDs harvested!

'''
import util
import sys
import gdata.docs.client
import ConfigParser
import psycopg2

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Plot Identifiers')
feed = docs_client.GetAllResources(query=query)

translate = {'column': 'col'}

lookup = {'tillage': 'TIL',
          'rotation': 'ROT',
          'drainage': 'DWM',
          'nitrogen': 'NIT',
          'landscape': 'LND'}

pcursor.execute("""DELETE from plotids""")
removed = pcursor.rowcount
added = 0
for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    worksheet = spreadsheet.worksheets['Sheet 1']
    for entry2 in worksheet.get_list_feed().entry:
        d = entry2.to_dict()
        cols = []
        vals = []
        for key in d.keys():
            v = None
            if d[key] is not None:                
                v = d[key].strip().replace("[", "").replace("]", "").split()[0]
                v = "%s%s" % (lookup.get(key, ''), v)
            if key == 'uniqueid':
                v = v.upper()
            vals.append( v )
            cols.append( translate.get(key,key) )
        sql = """INSERT into plotids(%s) VALUES (%s)""" % (",".join(cols),
                                                        ','.join(["%s"]*len(cols)))
        try:
            pcursor.execute(sql, vals)
        except Exception,exp:
            print exp
            print spreadsheet.title
            print cols
            sys.exit()
        added += 1
        
if removed > (added + 10):
    print 'Aborting harvest_plotids due to sz'
    sys.exit()
print "   harvest_plotids %s removed, %s added" % (removed,
                                                             added)
pcursor.close()
pgconn.commit()
pgconn.close()