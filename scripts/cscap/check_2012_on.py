"""
  Look at the Agronomic Sheets and see if the number of rows match between
  2011 and the rest of the years
"""
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.client
import gdata.gauth
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

# Get data spreadsheets
query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    print '------------>', spreadsheet.title
    worksheet = spreadsheet.worksheets['2011']
    rows = worksheet.rows
    for yr in ['2012', '2013', '2014', '2015']:
        worksheet = spreadsheet.worksheets[yr]
        if rows != worksheet.rows:
            print '    Year: %s has row count: %s , 2011 has: %s' % (yr,
                                            worksheet.rows, rows)
            
            