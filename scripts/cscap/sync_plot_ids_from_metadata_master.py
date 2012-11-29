"""
 Look at the metadata master table and see what our PI table is missing
 $Id: create_plot_ids.py 7800 2011-11-07 17:26:23Z akrherz $:
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

treat_feed = spr_client.get_list_feed(config.get('cscap', 'treatkey'), 'od6')
meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

headers = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage', 
           'Nitrogen', 'Landscape','My ID']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey is None or sitekey.upper() != 'DPAC':
        continue
    leadpi = data.get('leadpi')
    pi_spreadsheet = spr_client.get_list_feed( data.get('keyspread'), 'od6' )
    current_entries = []
    for le in pi_spreadsheet.entry:
        row = le.to_dict()
        key = "%s||%s||%s||%s||%s||%s" % (row.get('tillage',''), row.get('rotation','')
                    , row.get('nitrogen',''), row.get('landscape',''), 
                    row.get('rep',''), row.get('drainage', ''))
        current_entries.append( key.replace('None','').replace('none','') )
        
    
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
                            thisID = "%s||%s||%s||%s||%s||%s" % (treatment_names.get(till,''), 
                                                             treatment_names.get(rot,'')
                    , treatment_names.get(nit,''), treatment_names.get(lnd,''), 
                    treatment_names.get(drain,''), rep)
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
                            print 'Found new!', thisID, current_entries
                            
                            rows.append(entry)
    print len(current_entries)
    print pi_spreadsheet.get_id()
    for row in rows:
        spr_client.add_list_entry(row, 
                    '0AqZGw0coobCxdHpLSHlHM09pZTdYdjR2bEF5X2laZnc', 'od6')
