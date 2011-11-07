"""
 Something that will create dataspreadsheets based on entries in the table
 $Id$:
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

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                #access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

docs_client = gdata.docs.client.DocsClient()
token.authorize(docs_client)

query = gdata.docs.client.DocsQuery(show_collections='true', title='Synced Data')
feed = docs_client.GetAllResources(query=query)
sync_data = feed[0]

meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')
sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
treat_feed = spr_client.get_list_feed(config.get('cscap', 'treatkey'), 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)
sdc, sdc_names = util.build_sdc(sdc_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

baseheaders = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage', 'Nitrogen', 'Landscape','MyID']
basecolumns = {'A': 'UniqueID', 'B': 'Rep', 'C': 'Tillage', 'D': 'Rotation', 
           'E': 'Drainage', 'F': 'Nitrogen', 'G': 'Landscape','H': 'MyID'}

letters = ['I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
           'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey is None:
        continue
    leadpi = data.get('leadpi')
    
    # Lets go find the Plot Identifiers Table
    title = '%s %s Plot Identifiers' % (leadpi, sitekey.upper())
    query = gdata.docs.client.DocsQuery(show_collections='false', title=title)
    feed = docs_client.GetAllResources(query=query)
    spreadkey= feed[0].resource_id.text.split(':')[1]
    # loop over rows
    plots = []
    feed = spr_client.get_list_feed(spreadkey, 'od6')
    for feed_entry in feed.entry:
        plots.append( feed_entry.to_dict() )
        
    
    # Figure out our columns
    columns = basecolumns.copy()
    headers = baseheaders
    i = 0
    datavars = []
    for datavar in sdc[sitekey]:
        if datavar.find("AGR") > -1:
            #hid = '%s %s %s' % (datavar, sdc_names[datavar]['name'], sdc_names[datavar]['units'])
            hid = datavar
            columns[ letters[i] ] = hid
            datavars.append( hid )
            headers.append( hid )
            i += 1
    
    # Figure out how many 
    rows = []
    # Do row 2
    entry = gdata.spreadsheets.data.ListEntry()
    for dv in datavars:
        hid = '%s %s' % (sdc_names[dv]['name'], sdc_names[dv]['units'])
        entry.set_value(dv.lower(), hid)
    for col in plots[0].keys():
        entry.set_value(col, '')   
    rows.append(entry)
    for plot in plots:
        entry = gdata.spreadsheets.data.ListEntry()
        for dv in datavars:
            entry.set_value(dv.lower(), '')
        for col in plot.keys():
            entry.set_value(col, plot[col])    
        rows.append(entry)
    
    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Agronomic Data v2' % (leadpi, sitekey.upper())
    print 'Adding: %s ROWS: %s' %  (title, len(rows))
    doc = gdata.docs.data.Resource(type='spreadsheet', title=title)
    doc = docs_client.CreateResource(doc, collection=sync_data)
    spreadkey= doc.resource_id.text.split(':')[1]
    for yr in ['2011','2012','2013','2014','2015']:        
        sheet = spr_client.add_worksheet(spreadkey, yr, 10, len(columns))
    #sheet = spr_client.get_worksheet(spreadkey, 'od6')
    #tbl = spr_client.add_table(spreadkey, title, title, 'Sheet 1', 1,len(rows), 2, 'overwrite',
    #                     columns)
        for colnum in range(len(headers)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),1, colnum+1)
            cell.cell.input_value = headers[colnum]
            spr_client.update(cell)
        for row in rows:
            spr_client.add_list_entry(row, spreadkey, sheet.get_worksheet_id())
    #TODO remove first worksheet
    sheet = spr_client.get_worksheet(spreadkey,'od6')
    spr_client.delete(sheet)
    sys.exit()
