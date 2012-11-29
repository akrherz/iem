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

query = gdata.docs.client.DocsQuery(show_collections='true', title='Agronomic Data')
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    # Actually, it is just od7, od8, od9, od10, od11 (od6 was deleted)
    try:
        feed2 = spr_client.GetWorksheets(entry.id.text.split("/")[-1][14:])
    except:
        continue
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        feed3 = spr_client.get_list_feed(entry.id.text.split("/")[-1][14:], worksheet)
        row3 = feed3.entry[1]
        dict = row3.to_dict()
        if dict.get('agr31', None) is not None:
            row3.set_value('agr31', 'mg kg-1')
            spr_client.update(row3)
        
        """
        for entry3 in feed3.entry:
            dict = entry3.to_dict()
            val = dict.get('tillage', '')
            if val is not None and val.strip() == '[2] Conventional Tillage (CT) (chisel plow or disk and cultivate)':
                entry3.set_value('tillage', '[2] Conventional Tillage (CT)')
                spr_client.update(entry3)
        """