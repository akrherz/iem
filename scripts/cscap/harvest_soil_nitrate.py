'''
 Scrape out the Soil Nitrate data from Google Drive
'''
import util
import sys
import gdata.docs.client
import ConfigParser
import psycopg2

YEAR = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Soil Nitrate Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_cell_feed()
    siteid = spreadsheet.title.split()[0]
    #print 'Processing %s Soil Nitrate Year %s' % (siteid, YEAR),
    if worksheet.get_cell_value(1, 1) != 'plotid':
        print 'FATAL site: %s soil nitrate has corrupt headers' % (siteid,)
        continue
    startcol = 3
    if worksheet.get_cell_value(1,2) == 'depth':
        depthcol = 2
    elif worksheet.get_cell_value(1,3) == 'depth':
        depthcol = 3
        startcol = 4
    if worksheet.get_cell_value(1,2) == 'location':
        locationcol = 2
    else:
        locationcol = None

    for row in range(3, worksheet.rows+1):
        plotid = worksheet.get_cell_value(row, 1)
        depth = worksheet.get_cell_value(row, depthcol)
        if plotid is None or depth is None:
            continue
        subsample = "1"
        if locationcol is not None:
            subsample = worksheet.get_cell_value(row, locationcol)
        for col in range(startcol, worksheet.cols+1):
            varname = worksheet.get_cell_value(1, col).strip().split()[0]
            if varname[:4] != 'SOIL':
                print 'Invalid varname: %s site: %s year: %s' % (
                                    worksheet.get_cell_value(1,col).strip(),
                                    siteid, YEAR)
                continue
            val = worksheet.get_cell_value(row, col)
            try:
                pcursor.execute("""
                    INSERT into soil_data(site, plotid, varname, year, 
                    depth, value, subsample)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, depth, val, subsample))
            except Exception, exp:
                print 'site: %s year: %s HARVEST_SOIL_NITRATE TRACEBACK' % (
                                                    siteid, YEAR)
                print exp
                print '%s %s %s %s %s' % (siteid, plotid, varname, depth, val)
                sys.exit()
    #print "...done"
pcursor.close()
pgconn.commit()
pgconn.close()