"""
 Go thru the agronomic data sheets and replace the description label found on
 row 2 with a new value
"""
import gdata.docs.client
import ConfigParser

import util

VARID = 'agr43' # lowercase
NEWVAL = '[43] Red clover or mixed cover crop total carbon in late fall of previous year'

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='true', 
                                    title='NAEW Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    feed2 = spr_client.GetWorksheets(entry.id.text.split("/")[-1][14:])
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        print 'Processing %s WRK: %s Title: %s' % (entry.title.text, 
                                                   worksheet, entry2.title.text),
        feed3 = spr_client.get_list_feed(entry.id.text.split("/")[-1][14:], 
                                         worksheet)
        if len(feed3.entry) == 0:
            print 'Skipping as there is no data?!?'
            continue
        row = feed3.entry[0]
        data = row.to_dict()
        if data.get(VARID, None) is not None:
            row.set_value(VARID, NEWVAL)
            spr_client.update(row)
            print ' ... updated'
        else:
            print ' ... not found!'
