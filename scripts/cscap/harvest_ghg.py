'''
 Scrape out the GHG data from Google Drive
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
                                    title='%s GHG Data' % (YEAR,))
feed = docs_client.GetAllResources(query=query)

PIDS = util.get_xref_siteids_plotids(spr_client, config)

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    for wkey in spreadsheet.worksheets.keys():
        worksheet = spreadsheet.worksheets[wkey]
        worksheet.get_cell_feed()
        siteid = worksheet.title.strip()
        plotidcol = None
        for col in range(1, worksheet.cols+1):
            val = worksheet.get_cell_value(1, col)
            if val is None:
                continue
            if val.lower().find("plot id") == 0:
                plotidcol = col
            if (val.lower().find("sample key") == 0 or 
                val.lower().find("samplekey") == 0):
                plotidcol = col
        if plotidcol is None:
            print 'Site: %s is missing plotid column!' % (siteid,)
            continue
        plotids = []
        for row in range(3,worksheet.rows+1):
            plotid = worksheet.get_cell_value(row, plotidcol)
            if plotid is None:
                continue
            plotid = plotid.replace('band', '').replace('row', '')
            if plotid.lower().strip() not in plotids:
                plotids.append( plotid.lower().strip() )
                
        plotids.sort()
        for pid in plotids:
            if pid not in PIDS[siteid.lower()]:
                print 'Site: %s has unknown GHG %s Plot ID: %s' % (siteid,
                                                                   YEAR, pid)