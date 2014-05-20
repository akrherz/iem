'''
 Scrape out the Soil Nitrate data from Google Drive
'''
import util
import gdata.docs.client
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')


# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Soil Nitrate Data')
feed = docs_client.GetAllResources(query=query)

cols = []

seasons = {'SOIL15': "Spring",
           'SOIL22': 'Spring',
           'SOIL16': 'Summer',
           'SOIL23': 'Fall',
           'SOIL25': 'Fall'}

what = {'SOIL15': "Nitrate",
           'SOIL22': 'Ammonium',
           'SOIL16': 'Nitrate',
           'SOIL23': 'Nitrate',
           'SOIL25': 'Ammonium'}

def translate(year, oldval):
    ''' Convert something old into something new '''
    if oldval not in cols:
        cols.append( oldval )
    tokens = oldval.split()
    if tokens[0] in ['SOIL99', 'SOIL98', 'SOIL97', 'SOIL96']:
        return oldval
    cy = year
    if tokens[0] in ['SOIL23', 'SOIL25']:
        cy = int(year) - 1
    
    return "%s Calendar Year %s %s Soil %s" % (tokens[0], cy, 
                                            seasons[ tokens[0] ],
                                            what[ tokens[0]])
    

for entry in feed:
    if entry.get_resource_type() != 'spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    spreadsheet.get_worksheets()
    for year in spreadsheet.worksheets:
        worksheet = spreadsheet.worksheets[year]
        worksheet.get_cell_feed()
        for entry in worksheet.cell_feed.entry:
            if entry.cell.row != "1":
                continue
            val = entry.cell.input_value.strip()
            if val in ['plotid', 'depth']:
                continue
            newval = translate(year, val)
            if newval != val:
                print '[%s] %s -> %s' % (year, val, newval)
                entry.cell.input_value = newval
                spr_client.update(entry)
print cols