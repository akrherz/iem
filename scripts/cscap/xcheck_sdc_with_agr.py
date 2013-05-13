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
import copy

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
sdc, sdc_names = util.build_sdc(sdc_feed)


query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)
feed.reverse()
for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    sitekey = spreadsheet.title.split()[0].lower()
    print '------------>', sitekey, spreadsheet.title
    worksheet = spreadsheet.worksheets['2011']
    worksheet.get_list_feed()      
    entry2 = worksheet.list_feed.entry[0]
    data = entry2.to_dict()
    keys = data.keys()
    shouldhave = copy.deepcopy(sdc[sitekey])
    error = False
    for key in keys:
        if key.upper() not in shouldhave:
            if key.upper().find("AGR") == 0:
                print 'EXTRA %s' % (key.upper(),)
                error = True
        else:
            shouldhave.remove( key.upper() )
    for sh in shouldhave:
        if sh.find("AGR") == 0:
            print 'SHOULDHAVE %s' % (sh,)
            error = True
    if error:
        sys.exit()