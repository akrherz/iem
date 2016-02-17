"""Go through our data sheets and cleanup entries that don't exactly match
things that we would like to see"""
import pyiem.cscap_utils as util

config = util.get_config()
spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

# Fake last conditional to make it easy to reprocess one site...
res = drive.files().list(q=("title contains 'Soil Bulk Density' or "
                            "title contains 'Soil Nitrate Data' or "
                            "title contains 'Soil Texture Data' or "
                            "title contains 'Agronomic Data'"),
                         maxResults=999).execute()

HEADERS = ['uniqueid', 'plotid', 'depth', 'tillage', 'rotation', 'soil6',
           'nitrogen', 'drainage', 'rep', 'subsample', 'landscape',
           'notes', 'herbicide', 'sampledate']

sz = len(res['items'])
for i, item in enumerate(res['items']):
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    for year in spreadsheet.worksheets:
        print('%3i/%3i sheet "%s" for "%s"' % (i + 1, sz, year, item['title']))
        lf = spreadsheet.worksheets[year].get_list_feed()
        for rownum, entry in enumerate(lf.entry):
            dirty = False
            data = entry.to_dict()
            for key, value in data.iteritems():
                if key in HEADERS:
                    continue
                newvalue = value
                if value is None:
                    continue
                if value in ['N/A', 'NA', 'n/a', 'Grass, no crop']:
                    newvalue = 'n/a'
                elif value in ['.', '-', '..']:
                    newvalue = '.'
                elif value in ['Did not collect', 'DID NOT COLLECT',
                               'Did Not Collect', 'fire loss', 'dnc',
                               'did  not collect', 'Not collected',
                               'Farm sold', 'DNC', 'Drowned out',
                               'Farm was not available', 'did not collect',
                               'outlier', 'not collected', '#NUM!',
                               'no sample']:
                    newvalue = 'did not collect'
                else:
                    try:
                        float(value)
                    except:
                        if rownum > 1:
                            print("    invalid key:%s val:%s" % (key, value))
                        continue
                if newvalue != value:
                    entry.set_value(key, newvalue)
                    print('    key:%s "%s" -> "%s"' % (key, value, newvalue))
                    dirty = True
            if dirty:
                util.exponential_backoff(spr_client.update, entry)
