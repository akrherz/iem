import sys
import pyiem.cscap_utils as util
import copy
import re

VARNAME_RE = re.compile("^(SOIL[0-9]+)")

YEAR = sys.argv[1]

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)

sdc_feed = spr_client.get_list_feed(config['cscap']['sdckey'], 'od6')
sdc, sdc_names = util.build_sdc(sdc_feed)

drive_client = util.get_driveclient(config)

ALLOWED = ['SOIL1', 'SOIL2', 'SOIL29', 'SOIL30', 'SOIL31', 'SOIL32',
           'SOIL33', 'SOIL34', 'SOIL35', 'SOIL39']

res = drive_client.files().list(q=("title contains '%s'"
                                   ) % (('Soil Bulk Density and '
                                         'Water Retention Data'),)
                                ).execute()
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
        if not key.upper().startswith("SOIL"):
            continue
        varname = VARNAME_RE.findall(key.upper())[0]
        if varname not in shouldhave:
            vals = []
            for entry4 in worksheet.list_feed.entry:
                d = entry4.to_dict()
                if d[key] not in vals:
                    vals.append(d[key])
            print 'EXTRA %s' % (varname,), vals
            if len(vals) < 4:
                if raw_input("DELETE? y/n ") == 'y':
                    print("Deleting...")
                    worksheet.del_column(varname, sloppy=True)
                    worksheet.get_list_feed()
        else:
            shouldhave.remove(varname)
    for sh in shouldhave:
        if sh.find("SOIL") == 0 and sh in ALLOWED:
            print 'SHOULDHAVE %s' % (sh,)
            error = True
