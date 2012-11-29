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

replacements = {'0-10cm'  : '0 - 10',
                '10-20cm'  : '10 - 20',
                '20-40cm' : '20 - 40',
                '40-60cm': '40 - 60',
                "0-10": '0 - 10',
                "10-20": '10 - 20',
                "20-40": '20 - 40',
                "40-60": '40 - 60',
                "10/20/2012": '10 - 20',
                }

for entry in feed:
    # Actually, it is just od7, od8, od9, od10, od11 (od6 was deleted)
    try:
        feed2 = spr_client.GetWorksheets(entry.id.text.split("/")[-1][14:])
    except:
        continue
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        feed3 = spr_client.get_list_feed(entry.id.text.split("/")[-1][14:], worksheet)
        for entry3 in feed3.entry:
            dict = entry3.to_dict()
            entry3.set_value('depth', replacements.get(dict['depth'], dict['depth']))
            spr_client.update(entry3)