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

meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid')
    leadpi = data.get('leadpi')
    key = data.get('keyspread')
    title = '%s %s Plot Identifiers' % (sitekey.upper(), leadpi)
    print '<br><a href="https://docs.google.com/spreadsheet/ccc?key=%s">%s</a>' % (key, title,)