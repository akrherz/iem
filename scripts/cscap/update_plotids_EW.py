"""
 Go into the various sheets and replace the rotation text with something 
 explicit for the year
"""

import gdata.docs.client
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

# Get data spreadsheets 
query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='BRADFORD.B2 Scharf Soil Bulk Density')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    
    for yr in ['2011', ]:
        print '------------>', spreadsheet.title, yr
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            if data['rotation'] is None:
                continue
            if data['rotation'].find("CORN") > 0:
                plotid = data['plotid'] +'W'
            else:
                plotid = data['plotid'] +'E'
            if data['plotid'].find('E') > 0 or data['plotid'].find('W') > 0:
                continue
            print 'Rotation: %s Current: %s New: %s' % (data['rotation'],
                                                        data['plotid'], plotid)
            entry.set_value('plotid', plotid)
            spr_client.update(entry)
            