"""SWROC sites changed to HICKS"""
import util
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient()

# Fake last conditional to make it easy to reprocess one site...
res = drive.files().list(q=("(title contains 'Soil Bulk Density' or "
                            "title contains 'Soil Nitrate Data' or "
                            "title contains 'Soil Texture Data' or "
                            "title contains 'Agronomic Data' or "
                            "title contains 'Plot Identifiers') and "
                            "title contains 'HICKS'"),
                         maxResults=999).execute()

sz = len(res['items'])
for i, item in enumerate(res['items']):
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    for year in spreadsheet.worksheets:
        print('%3i/%3i sheet "%s" for "%s"' % (i + 1, sz, year, item['title']))
        lf = spreadsheet.worksheets[year].get_list_feed()
        for entry in lf.entry:
            dirty = False
            data = entry.to_dict()
            if data.get('uniqueid') is None:
                continue
            value = data['uniqueid']
            newvalue = value.replace("swroc", 'hicks')
            if newvalue != value:
                entry.set_value('uniqueid', newvalue)
                print('    "%s" -> "%s"' % (value, newvalue))
                util.exponential_backoff(spr_client.update, entry)
