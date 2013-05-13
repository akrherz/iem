"""
 Go into the various sheets and replace the rotation text with something 
 explicit for the year
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
    worksheet.get_list_feed()  
    match = []
    for entry in worksheet.list_feed.entry:
        data = entry.to_dict()
        match.append( data )
    for yr in ['2012', '2013', '2014', '2015']:
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        old = []
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            old.append( data )
            for key in data.keys():
                if key.find("AGR") == 0 and data[key] is not None:
                    print yr, key

        if len(match) != len(old):
            print 'Would rerun!'
            
            