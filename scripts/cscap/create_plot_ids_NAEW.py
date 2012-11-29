"""
 This will create spreadsheets based on the metadata table
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

query = gdata.docs.client.DocsQuery(show_collections='true', 
                                    title='Data Entry Spreadsheets')
feed = docs_client.GetAllResources(query=query)
sync_data = feed[0]

treat_feed = spr_client.get_list_feed(config.get('cscap', 'treatkey'), 'od6')
meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)

"""
Okay, we are cross product TIL x ROT x DWM x NIT
"""

headers = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage', 
           'Nitrogen', 'Landscape','My ID']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey is None or sitekey.find('vicms') == -1:
        continue
    leadpi = data.get('leadpi')
    colfolder = data.get('colfolder')
    collect = docs_client.get_resource_by_id(colfolder)
    
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
                            entry.set_value('tillage', treatment_names.get(till,''))
                            entry.set_value('rotation', treatment_names.get(rot,''))
                            entry.set_value('nitrogen', treatment_names.get(nit,''))
                            entry.set_value('landscape', treatment_names.get(lnd,''))
                            entry.set_value('drainage', treatment_names.get(drain,''))
                            entry.set_value('rep', str(rep))
                            entry.set_value('myid', '')
                            rows.append(entry)
    # Create the plots cross reference
    title = '%s %s Plot Identifiers' % (sitekey.upper(), leadpi)
    doc = gdata.docs.data.Resource(type='spreadsheet', title=title)
    doc = docs_client.CreateResource(doc, collection=collect)
    spreadkey= doc.resource_id.text.split(':')[1]
    sheet = 'od6'
    for colnum in range(len(headers)):
        cell = spr_client.get_cell(spreadkey, sheet,1, colnum+1)
        cell.cell.input_value = headers[colnum]
        spr_client.update(cell)
    for row in rows:
        spr_client.add_list_entry(row, spreadkey, sheet)
