import ConfigParser
import sys
import util  # @UnresolvedImport
import copy
import re

VARNAME_RE = re.compile("^(SOIL[0-9]+)")

YEAR = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)

sdc_feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
sdc, sdc_names = util.build_sdc(sdc_feed)

drive_client = util.get_driveclient()

ALLOWED = ['SOIL15', 'SOIL22']

res = drive_client.files().list(q=("title contains '%s'"
                                   ) % (('Soil Nitrate Data'),)
                                ).execute()
for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    sitekey = item['title'].split()[0].lower()
    print '------------> %s [%s] [%s]' % (YEAR, sitekey, item['title'])
    if YEAR not in spreadsheet.worksheets:
        print(('    skipping, year not in %s'
               ) % (str(spreadsheet.worksheets.keys()),))
        continue
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_cell_feed()
    worksheet.get_list_feed()
    if len(worksheet.list_feed.entry) == 0:
        print '    EMPTY sheet, skipping'
        continue
    header = ['']
    for col in range(1, worksheet.cols+1):
        header.append(worksheet.get_cell_value(1, col))
    shouldhave = copy.deepcopy(sdc[YEAR][sitekey])
    doeshave = []
    error = False
    for col, varname in enumerate(header):
        if not varname.startswith('SOIL'):
            continue
        soilcode = varname.split()[0]
        if soilcode in doeshave:
            continue
        if soilcode not in shouldhave:
            vals = []
            key = varname.lower().replace(" ", "").replace("/", "")
            for entry4 in worksheet.list_feed.entry:
                d = entry4.to_dict()
                if d[key] not in vals:
                    vals.append(d[key])
            print 'EXTRA %s[%s]' % (varname, soilcode)
            print vals
            if len(vals) < 4:
                if raw_input("DELETE? y/n ") == 'y':
                    print("Deleting... |%s|" % (varname, ))
                    worksheet.del_column(varname)
                    worksheet.get_list_feed()
        else:
            doeshave.append(soilcode)
            shouldhave.remove(soilcode)
    for sh in shouldhave:
        if sh.find("SOIL") == 0 and sh in ALLOWED:
            print 'SHOULDHAVE %s' % (sh,)
            error = True
