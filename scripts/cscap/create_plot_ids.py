"""
 This will create spreadsheets based on the metadata table
"""
import sys
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import pyiem.cscap_utils as util

print 'This is non-func, but worth while to keep around'
sys.exit()

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)

query = gdata.docs.client.DocsQuery(show_collections='true', 
                                    title='Data Spreadsheets')
feed = docs_client.GetAllResources(query=query)
sync_data = feed[0]

treat_feed = spr_client.get_list_feed(config['cscap']['treatkey'], 'od6')
meta_feed = spr_client.get_list_feed(config['cscap']['metamaster'], 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

headers = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage', 
           'Nitrogen', 'Landscape','My ID']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if data.get('keyspread') is not None:
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
                            entry.set_value('rep', str(rep))
                            entry.set_value('plot id', '')
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

    print 'Created %s keyspread: %s' % (title, spreadkey)
    #entry.set_value('keyspread', spreadkey)
    #spr_client.update(entry)
