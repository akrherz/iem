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


xref_feed = spr_client.get_list_feed(config.get('cscap', 'xrefrot'), 'od6')

rotations = {}

for entry in xref_feed.entry:
    data = entry.to_dict()

    rotations[ data['code'] ] = data

# Get data spreadsheets 
query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='NWREC Nafziger & Villamil Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    for yr in ['2011', '2012', '2013', '2014', '2015']:
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
            print data['rotation'], code, newval
            entry.set_value('rotation', newval)
            spr_client.update(entry)
            