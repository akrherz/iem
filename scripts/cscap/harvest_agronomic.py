"""
Harvest the Agronomic Data into the ISU Database
"""
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
                                    title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_cell_feed()
    siteid = spreadsheet.title.split()[0]
    for col in range(1, worksheet.cols+1):
        val = worksheet.get_cell_value(1, col)
        if val.find("PlotID") == 0:
            plotidcol = col
        if val.find("AGR") != 0:
            continue
        varname = val
        for row in range(4,worksheet.rows+1):
            plotid = worksheet.get_cell_value(row, plotidcol)
            if plotid is None:
                continue
            val = worksheet.get_cell_value(row, col)
            if val is not None and val.lower() in ['.', 'did not collect', 
                                                   'n/a']:
                val = None
            try:
                pcursor.execute("""
                    DELETE from agronomic_data WHERE site = %s and 
                    plotid = %s and varname = %s and year = %s
                """, (siteid, plotid, varname, YEAR))
                pcursor.execute("""
                    INSERT into agronomic_data(site, plotid, varname, year, value)
                    values (%s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, val))
            except Exception, exp:
                print 'HARVEST_AGRONOMIC TRACEBACK'
                print exp
                print '%s %s %s %s' % (siteid, plotid, varname, val)
                sys.exit()

pcursor.close()
pgconn.commit()
pgconn.close()