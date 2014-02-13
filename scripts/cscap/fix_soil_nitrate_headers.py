'''
 Scrape out the Soil Nitrate data from Google Drive
'''
import util
import sys
import gdata.docs.client
import ConfigParser
import psycopg2

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')


# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Soil Nitrate Data')
feed = docs_client.GetAllResources(query=query)

varconv = {'soil nitrate spring sampling': 'SOIL15',
           'soil nitrate summer sampling': 'SOIL16',
           'soil nitrate fall sampling': 'SOIL23'}

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    cols = []
    for key in spreadsheet.worksheets:
        worksheet = spreadsheet.worksheets[key]
        worksheet.get_cell_feed()
        for col in range(1, worksheet.cols+1):
            cell_feed = spr_client.get_cells(spreadsheet.id, 
                                             worksheet.id)
            for entry in cell_feed.entry:
                row = entry.cell.row
                if row != "1":
                    continue
                cv = entry.cell.input_value.strip()
                if cv not in cols:
                    cols.append(cv)
                if varconv.has_key(cv):
                    print 'Fixing %s [%s] %s' % (spreadsheet.title, key, cv)
                    entry.cell.input_value = "%s %s" % (varconv[entry.cell.input_value.strip()],
                                               entry.cell.input_value)
                    spr_client.update(entry)
    print spreadsheet.title, cols