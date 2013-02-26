"""
"""

import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import re
import ConfigParser
import sys
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='true', title='Soil Nitrate Data')
feed = docs_client.GetAllResources(query=query)

newcols = [
           ['SOIL22 Soil Ammonium (Optional)', 'mg per kg soil'],
           ]

for entry in feed:
    spreadkey = entry.id.text.split("/")[-1][14:]
    feed2 = spr_client.GetWorksheets( spreadkey )
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        print 'Processing %s WRK: %s Title: %s' % (entry.title.text, 
                                                   worksheet, entry2.title.text),
        feed3 = spr_client.get_list_feed(spreadkey, worksheet)
        row = feed3.entry[0]
        data = row.to_dict()
        #if data.get('agr6') is None and data.get('agr7') is None:
        #    print ' ... not found!'
        #    continue

        plusone = int(entry2.col_count.text) + 1
        entry2.col_count.text = str(plusone)
        spr_client.update(entry2)
        
        # Add a column?
        for i in range(len(newcols)):
            cell = spr_client.get_cell(spreadkey, worksheet,1, plusone-i)
            cell.cell.input_value = newcols[i][0]
            spr_client.update(cell)
    
            cell = spr_client.get_cell(spreadkey, worksheet,2, plusone-i)
            cell.cell.input_value = newcols[i][1]
            spr_client.update(cell)
    
        print ' ... updated'
        #sys.exit()
        
