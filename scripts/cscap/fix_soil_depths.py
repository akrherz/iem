"""Correct the labels used for soil depths in the sheets"""
import util
import ConfigParser
import sys

ALLOWED = ['depth (cm)', 'cm']

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient()

# Fake last conditional to make it easy to reprocess one site...
res = drive.files().list(q=("(title contains 'Soil Bulk Density' or "
                            "title contains 'Soil Nitrate Data' or "
                            "title contains 'Soil Texture Data') and "
                            "title contains 'Soil'"),
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
            current = entry.get_value('depth')
            if current is not None and current not in ALLOWED:
                if (len(current.split(" - ")) != 2 or current.find("cm") > 0 or
                        len(current) > 7):
                    tokens = current.replace("cm", "").strip().split("-")
                    if len(tokens) == 1:
                        if current.find("/") > 0:
                            tokens = current.split("/")[:2]
                        if len(tokens) == 1:
                            print('ERROR: "%s"' % (current, ))
                            sys.exit()
                    newval = '%s - %s' % (tokens[0].strip(),
                                          tokens[1].strip())
                    if newval != current:
                        entry.set_value('depth', newval)
                        print('    "%s" -> "%s"' % (current, newval))
                        spr_client.update(entry)
