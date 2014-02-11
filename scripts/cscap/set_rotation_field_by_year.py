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

xref_plotids = util.get_xref_plotids(spr_client, config)

xref_feed = spr_client.get_list_feed(config.get('cscap', 'xrefrot'), 'od6')

rotations = {}

for entry in xref_feed.entry:
    data = entry.to_dict()

    rotations[ data['code'] ] = data

# Get data spreadsheets 
query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    siteid = spreadsheet.title.split()[0]
    if siteid in ['VICMS',]:
        continue
    plotid_feed = spr_client.get_list_feed(xref_plotids[siteid], 'od6')
    plotids = {}
    for entry2 in plotid_feed.entry:
        row = entry2.to_dict()
        plotids[ row['plotid'] ] = row['rotation'].split()[0].replace("[", 
                                                    "").replace("]", "")
    
    for yr in ['2011', '2012', '2013', '2014', '2015']:
    #for yr in ['2011', ]:
        print '------------>', spreadsheet.title, yr
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            if data['uniqueid'] is None:
                continue
            code = data['rotation'].split()[0].replace("[", "").replace("]", 
                                                        "").replace("ROT", "")
            newval = "ROT%s :: %s" % (code,  rotations["ROT"+code]["y"+yr])
            if plotids[data['plotid']] != code:
                print 'Plot:%s Rotation PlotIdSheet->%s AgSheet->%s' % (
                        data['plotid'], plotids[data['plotid']], code)
            if newval != data['rotation']:
                print 'Plot:%s new:%s old:%s' % (data['plotid'], newval,
                                                 data['rotation'])
                entry.set_value('rotation', newval)
                spr_client.update(entry)
            