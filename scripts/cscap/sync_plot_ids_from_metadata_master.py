"""
 Look at the metadata master table and see what our PI table is missing
"""
import gdata.spreadsheets.data
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')


spr_client = util.get_spreadsheet_client(config)

treat_feed = spr_client.get_list_feed(config.get('cscap', 'treatkey'), 'od6')
meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

headers = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage',
           'Nitrogen', 'Landscape', 'My ID']


def get_just_code(text):
    if text == '':
        return ''
    return text.split()[0]

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey is None:
        continue
    print sitekey
    leadpi = data.get('leadpi')
    pi_spreadsheet = spr_client.get_list_feed(data.get('keyspread'), 'od6')
    current_entries = []
    for le in pi_spreadsheet.entry:
        row = le.to_dict()
        for key in row:
            if row[key] is None:
                row[key] = ''
        key = "%s||%s||%s||%s||%s||%s" % (
                    get_just_code(row.get('tillage').strip()),
                    get_just_code(row.get('rotation').strip()),
                    get_just_code(row.get('nitrogen').strip()),
                    get_just_code(row.get('landscape').strip()),
                    get_just_code(row.get('drainage').strip()),
                    row.get('rep').strip())
        current_entries.append(key.replace('None', '').replace('none', ''))

    # Figure out how many
    rows = []
    trt = treatments[sitekey]
    for k in ['TIL', 'ROT', 'DWM', 'NIT', 'LND']:
        if len(trt[k]) > 1:
            trt[k].remove(None)

    for till in trt['TIL']:
        for rot in trt['ROT']:
            for drain in trt['DWM']:
                for nit in trt['NIT']:
                    for lnd in trt['LND']:
                        for rep in range(1, trt['REPS'] +1):
                            thisID = "%s||%s||%s||%s||%s||%s" % (
                                    get_just_code(treatment_names.get(till,'')), 
                                    get_just_code(treatment_names.get(rot,'')), 
                                    get_just_code(treatment_names.get(nit,'')), 
                                    get_just_code(treatment_names.get(lnd,'')), 
                                    get_just_code(treatment_names.get(drain,'')), 
                                    rep)
                            if thisID in current_entries:
                                #print 'DUP!', thisID
                                current_entries.remove(thisID)
                                continue
                            entry = gdata.spreadsheets.data.ListEntry()
                            entry.set_value('uniqueid', sitekey)
                            entry.set_value('tillage', treatment_names.get(till,''))
                            entry.set_value('rotation', treatment_names.get(rot,''))
                            entry.set_value('nitrogen', treatment_names.get(nit,''))
                            entry.set_value('landscape', treatment_names.get(lnd,''))
                            entry.set_value('drainage', treatment_names.get(drain,''))
                            entry.set_value('rep', str(rep))
                            #entry.set_value('myid', '')
                            print 'Found new!'
                            print thisID
                            print current_entries

                            rows.append(entry)
    #print len(current_entries), sitekey
    #print pi_spreadsheet.get_id()
#    for row in rows:
#        spr_client.add_list_entry(row, 
#                    '0AqZGw0coobCxdHpLSHlHM09pZTdYdjR2bEF5X2laZnc', 'od6')
