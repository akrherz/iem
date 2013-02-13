"""
Rip and replace
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

query = gdata.docs.client.DocsQuery(show_collections='true', title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    feed2 = spr_client.GetWorksheets(entry.id.text.split("/")[-1][14:])
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        print 'Processing %s WRK: %s Title: %s' % (entry.title.text, 
                                                   worksheet, entry2.title.text),
        feed3 = spr_client.get_list_feed(entry.id.text.split("/")[-1][14:], worksheet)
        row = feed3.entry[0]
        data = row.to_dict()
        if data.get('agr7', None) is not None:
            row.set_value('agr7', '[7] Cover crop (rye) biomass at termination (spring) (no significant weeds)')
            spr_client.update(row)
            print ' ... updated'
        else:
            print ' ... not found!'
        
