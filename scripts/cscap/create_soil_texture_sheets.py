"""
 Something that will create soil texture sheets
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

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

docs_client = gdata.docs.client.DocsClient()
token.authorize(docs_client)

meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')
sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
treat_feed = spr_client.get_list_feed(config.get('cscap', 'treatkey'), 'od6')


DONE = ['gilmore',]

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey in DONE:
        print 'skip', sitekey
        continue
    # This is the folder where synced data is stored
    colfolder = data.get('colfolder')
    collect = docs_client.get_resource_by_id(colfolder)
    leadpi = data.get('leadpi')
    
    # Lets go find the Plot Identifiers Table
    keyspread = data.get('keyspread')
    # loop over rows
    plots = []
    feed = spr_client.get_list_feed(keyspread, 'od6')
    for feed_entry in feed.entry:
        cols = feed_entry.to_dict()
        if cols.get('plotid', '') not in ['', None]:
            plots.append( cols.get('plotid') )
    
    if len(plots) == 0:
        print 'No plot IDs found for: %s %s' % (leadpi, sitekey.upper())
        continue
    
    # Figure out our columns
    columns = ['plotid', 'depth', 'date', 'percent sand', ' percent silt', ' percent clay', 'texture']
    headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    depths = ['0-4"', '4-8"', '8-16"', '16-24"']

    # Figure out how many 
    rows = []
    for plot in plots:
        for depth in depths:
            entry = gdata.spreadsheets.data.ListEntry()
            for col in columns:
                entry.set_value(col.replace(" ", ''), '')
            entry.set_value('depth', depth)
            entry.set_value('plotid', plot)
            rows.append( entry )
    
    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Soil Texture Data' % (sitekey.upper(), leadpi)
    print 'Adding %s Rows: %s' % (title, len(rows))
    doc = gdata.docs.data.Resource(type='spreadsheet', title=title)
    doc = docs_client.CreateResource(doc, collection=collect)
    spreadkey= doc.resource_id.text.split(':')[1]
    for yr in ['2011',]:        
        print 'Adding worksheet for year: %s' % (yr,)
        sheet = spr_client.add_worksheet(spreadkey, yr, 10, len(columns))
        for colnum in range(len(columns)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),1, colnum+1)
            cell.cell.input_value = columns[colnum]
            spr_client.update(cell)
        for row in rows:
            spr_client.add_list_entry(row, spreadkey, sheet.get_worksheet_id())
    #TODO remove first worksheet
    sheet = spr_client.get_worksheet(spreadkey,'od6')
    spr_client.delete(sheet)
