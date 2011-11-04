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

def build_sdc(feed):
    """
    Process the Site Data Collected spreadsheet
    @param feed the processed spreadsheet feed
    """
    data = None
    sdc_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = []
        if row['key'] is None or row['key'] == '':
            continue
        sdc_key = row['key']
        sdc_names[sdc_key] = row['name']
        for sitekey in row.keys():
            if sitekey in data.keys():
                if row[sitekey] is not None and row[sitekey] != '':
                    data[sitekey].append( sdc_key )
    return data, sdc_names

def build_treatments(feed):
    """
    Process the Treatments spreadsheet and generate a dictionary of
    field metadata
    @param feed the processed spreadsheet feed
    """
    data = None
    treatment_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = {'TIL': [None,], 'ROT': [None,], 'DWM': [None,], 'NIT': [None,], 
                             'LND': [None,], 'REPS': 1}
        if row['key'] is None or row['key'] == '':
            continue
        treatment_key = row['key']
        treatment_names[treatment_key] = row['name']
        for colkey in row.keys():
            cell = row[colkey]
            if colkey in data.keys(): # Is sitekey
                sitekey = colkey
                if cell is not None and cell != '':
                    if treatment_key[:3] in data[sitekey].keys():
                        data[sitekey][treatment_key[:3]].append( treatment_key )
                if treatment_key == 'REPS' and cell != '?':
                    print 'Found REPS for site: %s as: %s' % (sitekey, int(cell))
                    data[sitekey]['REPS'] = int(cell)
    
    return data, treatment_names

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                access_token=config.get('googleauth', 'access_token'),
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

treatments, treatment_names = build_treatments(treat_feed)
sdc, sdc_names = build_sdc(sdc_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

baseheaders = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage', 'Nitrogen', 'Landscape']
basecolumns = {'A': 'UniqueID', 'B': 'Rep', 'C': 'Tillage', 'D': 'Rotation', 
           'E': 'Drainage', 'F': 'Nitrogen', 'G': 'Landscape'}

letters = ['H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
           'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey is None:
        continue
    leadpi = data.get('leadpi')
    
    # Figure out our columns
    columns = basecolumns.copy()
    headers = baseheaders
    i = 0
    datavars = []
    for datavar in sdc[sitekey]:
        if datavar.find("AGR") > -1:
            columns[ letters[i] ] = datavar
            datavars.append( datavar )
            headers.append( datavar )
            i += 1
    
    # Figure out how many 
    rows = []
    trt = treatments[sitekey]
    for k in ['TIL','ROT','DWM','NIT','LND']:
        if len(trt[k]) > 1:
            trt[k].remove(None)
            
    for till in trt['TIL']:
        for rot in trt['ROT']:
            for drain in trt['DWM']:
                for nit in trt['NIT']:
                    for lnd in trt['LND']:
                        for rep in range(1, trt['REPS'] +1):
                            entry = gdata.spreadsheets.data.ListEntry()
                            entry.set_value('uniqueid', sitekey)
                            entry.set_value('tillage', till or '')
                            entry.set_value('rotation', rot or '')
                            entry.set_value('nitrogen', nit or '')
                            entry.set_value('landscape', lnd or '')
                            entry.set_value('rep', str(rep))
                            for dv in datavars:
                                entry.set_value(dv.lower(), 'M')
                            rows.append(entry)
    
    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Agronomic Data' % (leadpi, sitekey.upper())
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
