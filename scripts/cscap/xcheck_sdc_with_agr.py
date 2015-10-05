"""
 Use the Site Data Collected and then see what columns exist within the
 Agronomic Data Sheets.
"""
import ConfigParser
import sys
import util
import copy

YEAR = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)

sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
sdc, sdc_names = util.build_sdc(sdc_feed)
print sdc['2015'].keys()

drive_client = util.get_driveclient()

res = drive_client.files().list(q="title contains 'Agronomic Data'").execute()
for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    sitekey = item['title'].split()[0].lower()
    print '------------> %s [%s] [%s]' % (YEAR, sitekey, item['title'])
    if YEAR not in spreadsheet.worksheets:
        print('%s does not have Year: %s in worksheet' % (sitekey, YEAR))
        continue
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_list_feed()
    if len(worksheet.list_feed.entry) == 0:
        print '    EMPTY sheet, skipping'
        continue
    entry2 = worksheet.list_feed.entry[0]
    data = entry2.to_dict()
    keys = data.keys()
    shouldhave = copy.deepcopy(sdc[YEAR][sitekey])
    error = False
    for key in keys:
        if key.upper() not in shouldhave:
            if key.upper().find("AGR") == 0:
                print 'EXTRA %s' % (key.upper(),)
                error = True
        else:
            shouldhave.remove(key.upper())
    for sh in shouldhave:
        if sh.find("AGR") == 0:
            print 'SHOULDHAVE %s' % (sh,)
            error = True
