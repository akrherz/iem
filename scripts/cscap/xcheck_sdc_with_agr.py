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

YEAR = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
sdc, sdc_names = util.build_sdc(sdc_feed)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='SWROC.G Agronomic Data')
feed = docs_client.GetAllResources(query=query)
feed.reverse()
for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    sitekey = spreadsheet.title.split()[0].lower()
    print '------------> %s [%s] [%s]' % ( YEAR, sitekey, spreadsheet.title)
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_list_feed()
    if len(worksheet.list_feed.entry) == 0:
        print '    EMPTY sheet, skipping'
        continue
    entry2 = worksheet.list_feed.entry[0]
    data = entry2.to_dict()
    keys = data.keys()
    shouldhave = copy.deepcopy(sdc[YEAR][sitekey])
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
            #worksheet.add_column(sh, sdc_names[sh]['name'], sdc_names[sh]['units'])
    #if error:
    #    sys.exit()