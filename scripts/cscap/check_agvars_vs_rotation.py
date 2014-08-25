import gdata.docs.client
import ConfigParser
import util
import sys

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

# Build xref of cropmate with variables
cropmates = {}
xref_feed = spr_client.get_list_feed(config.get('cscap', 'xrefrotvars'), 'od6')
for entry in xref_feed.entry:
    data = entry.to_dict()
    if not cropmates.has_key(data['cropmate']):
        cropmates[data['cropmate']] = []
    cropmates[ data['cropmate'] ].append( data['variable'].lower() )


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
    plotid_feed = spr_client.get_list_feed(xref_plotids[siteid], 'od6')
    plotids = {}
    for entry2 in plotid_feed.entry:
        row = entry2.to_dict()
        if not row.has_key('rotation'):
            print 'Invalid headers in plotid sheet for %s\n headers: %s' % (
                                                        spreadsheet.title,
                                                        " ".join(row.keys()))
            sys.exit()
            
        plotids[ row['plotid'] ] = row['rotation'].split()[0].replace("[",
                                                    "").replace("]", "")

    for yr in ['2011', '2012', '2013','2014', '2015' ]:
        ylookup = 'y%s' % (yr,)
        print '------------>', spreadsheet.title, yr
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            if data['plotid'] is None:
                continue
            rlookup = 'ROT%s' % (plotids[data['plotid']],)
            crop = rotations[rlookup][ylookup]
            dirty = False
            for col in data.keys():
                if col[:3] != 'agr':
                    continue
                #if (col in cropmates.get(crop, []) and data[col] == "."):
                #    print 'Setting to DNC', data['plotid'], crop, col, data[col]
                #    entry.set_value(col, 'did not collect')
                #    dirty = True                    
                if (col not in cropmates.get(crop, []) and 
                    (data[col] is None or 
                    data[col].lower() in ['.', 'did not collect'])):
                    print 'Setting to n/a', data['plotid'], crop, col, data[col]
                    entry.set_value(col, 'n/a')
                    dirty = True
                if data[col] is None:
                    continue
                    #print 'Setting to .', data['plotid'], crop, col
                    #entry.set_value(col, '.')
                    #dirty = True
                elif (col not in cropmates.get(crop, []) and 
                    data[col].lower() not in ['.', 'did not collect', 'n/a']):
                    print "PlotID: %s crop: %s has data [%s] for %s" % (
                                        data['plotid'], crop, data[col], 
                                        col.upper())
            if dirty:
                spr_client.update(entry)
