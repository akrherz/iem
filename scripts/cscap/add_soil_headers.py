"""
Rip and replace
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

query = gdata.docs.client.DocsQuery(show_collections='true', title='Soil Texture Data')
feed = docs_client.GetAllResources(query=query)

columns = [3,4,5,6,7,8,9,10]
labels = ['percent sand', 'percent silt', 'percent clay', 'texture', 
          'pH', 'Cation Exchange Capacity (cmol kg-1)', 'Soil Organic Carbon (%)', 
          'Total N (%)']

for entry in feed:
    spreadkey = entry.id.text.split("/")[-1][14:]
    feed2 = spr_client.GetWorksheets(spreadkey)
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        for i in range(len(columns)):
            print i, spreadkey, labels[i]
            cell = spr_client.get_cell(spreadkey, worksheet,1, i+3)
            cell.cell.input_value = labels[i]
            spr_client.update(cell)
            
            