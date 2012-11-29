import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import re
import ConfigParser
import pdb

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing22',
                                scope=config.get('googleauth', 'scopes'),
                                access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

docs_client = gdata.docs.client.DocsClient()
token.authorize(docs_client)
spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

doc = gdata.docs.data.Resource(type='spreadsheet', title='DARYL API TESTING')
doc = docs_client.CreateResource(doc)
spreadkey= doc.resource_id.text.split(':')[1]

#ws = spr_client.add_worksheet(spreadkey, 'YO YO', 10, 1)
entry = spr_client.get_cell(spreadkey,'od6',1,1)
entry.cell.input_value = 'Hi Daryl'
spr_client.update(entry)

entry = gdata.spreadsheets.data.ListEntry()
entry.set_value('hidaryl', 'row2')
spr_client.add_list_entry(entry, spreadkey, 'od6' )


feeds = spr_client.get_list_feed(spreadkey, 'od6')
for feed in feeds.entry:
    print feed

#entry = gdata.spreadsheets.data.ListEntry()
#entry.set_value('A', 'Hi Daryl')
#spr_client.add_list_entry(entry, spreadkey, ws.get_worksheet_id() )

#query = gdata.docs.client.DocsQuery(show_collections='true', title='DARYL')
#feed = docs_client.GetAllResources(query=query)



#spreadkey = '0AqZGw0coobCxdFR4MlkzZWdYQTU5b1l5UDhvWm5ZaHc'
#tbl = '0'
#row = {'nitrogen': 'NIT2', 'agr17': 'M', 'agr10': 'M', 'agr11': 'M', 'agr12': 'M', 'agr18': 'M', 'agr19': 'M', 'landscape': ' ', 'rep': '1', 'agr30': 'M', 'tillage': 'TIL1', 'agr8': 'M', 'agr9': 'M', 'agr4': 'M', 'agr5': 'M', 'agr2': 'M', 'agr1': 'M', 'uniqueid': 'nwrec', 'rotation': 'ROT1', 'agr29': 'M', 'agr28': 'M', 'agr25': 'M', 'agr24': 'M', 'agr27': 'M', 'agr26': 'M', 'agr21': 'M', 'agr20': 'M', 'agr23': 'M', 'agr22': 'M', 'drainage': 'DWM4'}


#print feed[0].resource_id.text.split(':')[1]

#rec = spr_client.get_tables(spreadkey)
#print rec
#spr_client.add_record(spreadkey, tbl, row)
#entry = gdata.spreadsheets.data.ListEntry()
#for k in row.keys():
#    entry.set_value(k, row[k])
#spr_client.add_list_entry(entry, spreadkey, 'od6')