"""

$Id: $:
"""

import gdata.spreadsheets.client
import gdata.gauth
import re
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

# Site Data Collected == sdc
meta_feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')

for entry in meta_feed.entry:
    data = entry.to_dict()
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    

    
    """
    lat = data.get('latitude')
    lon = data.get('longitude')
    tokens = re.findall("([0-9\.]+)", lon)
    if len(tokens) == 3:
        newval = 0 - ((float(tokens[2]) / 60.0 + float(tokens[1])) / 60.0 + float(tokens[0]))
        print lon, newval 
        entry.set_value('longitude', str(newval))
        spr_client.update(entry)
    """
#for d in spr_client.get_spreadsheets().entry:
#    if d.title.text.find("Field Log") > -1:
#        s = d.get_spreadsheet_key()


#for s in ['0AqZGw0coobCxdDlUZFdxSzJ4cmFHcXhqbkJzdUdZVVE', '0AqZGw0coobCxdG1fV3BOZnRqVEw5X1FfanFUUHh2LWc']:
    # Get metadata on spreadsheet
        #worksheet = spr_client.get_worksheet(s, 'od6')
        #for entry in spr_client.get_list_feed(s, 'od6').entry:
        #    data = entry.to_dict()
        #    print '%s,%s,%s' % (d.title.text, data.get('date', 'date'), data.get('log', 'log'))
            #print entry.to_dict()
        #entry.set_value('weight', '600')
        #print dir(entry)
        #print entry.title
        #spr_client.update(entry)
    #print entry.title

#print dir(spr_client)

#dict = {}
#dict['date'] = time.strftime('%m/%d/%Y')
#dict['time'] = time.strftime('%H:%M:%S')
#dict['weight'] = '100'

#entry = spr_client.InsertRow(dict, '0AqZGw0coobCxdElnVW4tWlRLN1BSaHltajYtR1FXakE', 'od6')
#if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
#  print "Insert row succeeded."
#else:
#  print "Insert row failed."