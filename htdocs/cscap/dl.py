#!/usr/bin/python
"""
 1. Connect to google spreadsheets and get me data!
$Id$:
"""

import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import ConfigParser

def response(text):
    """
    Return the http response
    """
    print 'Content-type: text/html\n'
    print
    print '<html><head><title>CSCAP Download</title></head>'
    print '<body>'
    print text
    print '</body>'
    print '</html>'
    
def get_data():
    """
    Go to Google and demand my data back!
    """
    res = ""
    config = ConfigParser.ConfigParser()
    config.read('/mesonet/www/apps/iemwebsite/scripts/cscap/mytokens.cfg')

    token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                    client_secret=config.get('appauth', 'app_secret'),
                    user_agent='daryl.website',
                    scope=config.get('googleauth', 'scopes'),
                    refresh_token=config.get('googleauth', 'refresh_token'))
    spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
    token.authorize(spr_client)
    # Hard Code Nafziger for now
    datakey = '0AqZGw0coobCxdC1sZ3l0RmFsV0hfekoyc2JYdHBxQ2c'
    res += "<table border='1' cellspacing='0' cellpadding='2'><tr><th>Year</th><th>Site</th><th>Tillage</th><th>AGR1</th></tr>"
    
    feed = spr_client.get_worksheets(datakey)
    for entry in feed.entry:
        sheetkey = entry.get_worksheet_id() 
        datafeed = spr_client.get_list_feed(datakey, sheetkey)
        for dataentry in datafeed.entry:
            data = dataentry.to_dict()
            if data.get('tillage') is None:
                continue
            res += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                                entry.title, data.get('uniqueid'),
                                data.get('tillage'),
                                data.get('agr1') or 'M')
    res += "</table>"
    return res
    
if __name__ == '__main__':
    res = get_data()
    response(res)
