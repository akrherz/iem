"""
 Something that will create soil texture sheets
"""
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import ConfigParser

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


DONE = ['onfarm.preble', 'onfarm.miami', 'onfarm.seneca1', 'onfarm.seneca2',
        'onfarm.auglaize', 'onfarm.logan1', 'onfarm.logan2']

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
    columns = ['plotid', 'depth', 'SOIL26', 'SOIL27', 'SOIL28', 'SOIL6',
               'SOIL11', 'SOIL12', 'SOIL13', 'SOIL14']
    columns2 = ['', '', 'percent sand', ' percent silt', ' percent clay', 'texture',
                'pH', 'Cation Exchange Capacity', 'Soil Organic Carbon',
                'Total N']
    columns3 = ['plotid',    'depth (cm)',    'percent sand',    
                'percent silt',    'percent clay',    'texture',    
                'pH',    'cmol kg-1',    '%',    '%']
    headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    depths = ['0-10', '10-20', '20-40', '40-60']

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
    for yr in ['2011', '2013', '2015']:        
        print 'Adding worksheet for year: %s' % (yr,)
        sheet = spr_client.add_worksheet(spreadkey, yr, 10, len(columns))
        for colnum in range(len(columns)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),1, colnum+1)
            cell.cell.input_value = columns[colnum]
            spr_client.update(cell)
        for colnum in range(len(columns2)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),
                                       2, colnum+1)
            cell.cell.input_value = columns2[colnum]
            spr_client.update(cell)
        for colnum in range(len(columns3)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),
                                       3, colnum+1)
            cell.cell.input_value = columns3[colnum]
            spr_client.update(cell)
        for row in rows:
            spr_client.add_list_entry(row, spreadkey, sheet.get_worksheet_id())
    #TODO remove first worksheet
    sheet = spr_client.get_worksheet(spreadkey,'od6')
    spr_client.delete(sheet)
