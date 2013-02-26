"""
 Something that will create soil nitrates
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

sdc_data, sdc_names = util.build_sdc(sdc_feed)

DONE = ['arl', 'lan']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey not in DONE:
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
    columns = ['plotid', 'depth', 'subsample', 'Bulk Density', 'Water Retention at 0 bar',
               'Water Retention at 0.05 bar', 'Water Retention at 0.1 bar', 'Water Retention at 0.33 bar',
               'Water Retention at 15 bar']
    units = ['', 'cm', 'number', 'g cm-3','', '','','','' ]
    depths = ['0 - 10', '10 - 20', '20 - 40', '40 - 60']

    # Figure out how many 
    rows = []

    # Do row1
    entry = gdata.spreadsheets.data.ListEntry()
    for col, unit in zip(columns, units):
        entry.set_value(col.replace(" ", '').lower(), unit)
    rows.append( entry )

    for plot in plots:
        for depth in depths:
            for sample in range(1,4):
                entry = gdata.spreadsheets.data.ListEntry()
                for col in columns:
                    entry.set_value(col.replace(" ", '').lower(), '')
                entry.set_value('depth', depth)
                entry.set_value('plotid', plot)
                entry.set_value('subsample', str(sample))
                rows.append( entry )
    
    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Soil Bulk Density and Water Retention Data' % (sitekey.upper(), leadpi)
    print 'Adding %s Rows: %s' % (title, len(rows))
    doc = gdata.docs.data.Resource(type='spreadsheet', title=title)
    doc = docs_client.CreateResource(doc, collection=collect)
    spreadkey= doc.resource_id.text.split(':')[1]
    for yr in ['2011','2012','2013','2014','2015']:        
        print '%s Adding worksheet for year: %s' % (spreadkey, yr)
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
