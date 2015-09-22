"""
  This script updates the data dashboard
"""
import util
import sys
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

YEAR = sys.argv[1]

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient()

ss = util.Spreadsheet(spr_client, config.get('cscap', 'dashboard'))
SHEET = ss.worksheets[YEAR]
SHEET.get_cell_feed()

column_ids = [""] * 100
for col in range(1, SHEET.cols+1):
    entry = SHEET.get_cell_entry(1, col)
    pos = entry.title.text
    text = entry.cell.input_value
    column_ids[int(entry.cell.col)] = text

lookuprefs = {
              'agr1': 'Agronomic Data',
              'agr2': 'Agronomic Data',
              'agr3': 'Agronomic Data',
              'agr4': 'Agronomic Data',
              'agr5': 'Agronomic Data',
              'agr6': 'Agronomic Data',
              'agr7': 'Agronomic Data',
              'agr8': 'Agronomic Data',
              'agr9': 'Agronomic Data',
              'agr10': 'Agronomic Data',
              'agr11': 'Agronomic Data',
              'agr12': 'Agronomic Data',
              'agr13': 'Agronomic Data',
              'agr14': 'Agronomic Data',
              'agr15': 'Agronomic Data',
              'agr16': 'Agronomic Data',
              'agr17': 'Agronomic Data',
              'agr18': 'Agronomic Data',
              'agr19': 'Agronomic Data',
              'agr20': 'Agronomic Data',
              'agr21': 'Agronomic Data',
              'agr22': 'Agronomic Data',
              'agr23': 'Agronomic Data',
              'agr24': 'Agronomic Data',
              'agr25': 'Agronomic Data',
              'agr26': 'Agronomic Data',
              'agr27': 'Agronomic Data',
              'agr28': 'Agronomic Data',
              'agr29': 'Agronomic Data',
              'agr30': 'Agronomic Data',
              'agr31': 'Agronomic Data',
              'agr32': 'Agronomic Data',
              'agr33': 'Agronomic Data',
              'agr34': 'Agronomic Data',
              'agr37': 'Agronomic Data',
              'agr38': 'Agronomic Data',
              'agr39': 'Agronomic Data',
              'agr40': 'Agronomic Data',
              'agr41': 'Agronomic Data',
              'agr42': 'Agronomic Data',
              'agr43': 'Agronomic Data',
              'agr44': 'Agronomic Data',
              'agr45': 'Agronomic Data',
              'agr46': 'Agronomic Data',
              'agr47': 'Agronomic Data',
              'agr48': 'Agronomic Data',
              'agr49': 'Agronomic Data',
              'soil1': 'Soil Bulk Density and Water Retention Data',
              'soil2': 'Soil Bulk Density and Water Retention Data',
              'soil29': 'Soil Bulk Density and Water Retention Data',
              'soil30': 'Soil Bulk Density and Water Retention Data',
              'soil31': 'Soil Bulk Density and Water Retention Data',
              'soil32': 'Soil Bulk Density and Water Retention Data',
              'soil33': 'Soil Bulk Density and Water Retention Data',
              'soil11': 'Soil Texture Data',
              'soil12': 'Soil Texture Data',
              'soil13': 'Soil Texture Data',
              'soil14': 'Soil Texture Data',
              'soil15': 'Soil Nitrate Data',
              'soil16': 'Soil Nitrate Data',
              'soil22': 'Soil Nitrate Data',
              'soil23': 'Soil Nitrate Data',
              'soil24': 'Soil Nitrate Data',
              'soil25': 'Soil Nitrate Data',
              'soil26': 'Soil Texture Data',
              'soil27': 'Soil Texture Data',
              'soil28': 'Soil Texture Data',
              }
varconv = {
           }

CACHE = {}
QUERY_CACHE = {}


def docs_query(title):
    """ Make sure we fetch the exact title from Google """
    if title in QUERY_CACHE:
        return QUERY_CACHE[title]

    res = drive_client.files().list(q="title contains '%s'" % (title,)
                                    ).execute()
    if len(res) > 1:
        delpos = None
        for i, item in enumerate(res['items']):
            if item['title'].split()[0] != title.split()[0]:
                delpos = i
        if delpos is not None:
            del(res['items'][delpos])
    if len(res['items']) == 0:
        print 'Could not find spreadsheet |%s|' % (title,)
        QUERY_CACHE[title] = []
        return []
    QUERY_CACHE[title] = res['items'][0]
    return res['items'][0]


def do_row(row):
    """ Actually process a row in the SHEET """
    firstcolumn = SHEET.get_cell_entry(row, 1)
    varname = firstcolumn.cell.input_value.split()[0].lower()
    spreadtitle = lookuprefs.get(varname)
    if spreadtitle is None:
        print 'ERROR: Do not know how to reference %s in lookuprefs' % (
                                                                varname,)
        return

    for col in range(2, SHEET.cols+1):
        entry = SHEET.get_cell_entry(row, col)
        if entry is None:
            print 'Found none type entry? row: %s col: %s' % (row, col)
        siteid = column_ids[int(entry.cell.col)]
        if siteid in ['', 'Required (R)']:
            continue

        querytitle = '%s %s' % (siteid, spreadtitle)
        resources = docs_query(querytitle)
        if len(resources) == 0:
            continue
        skey = resources['id']
        if skey in CACHE:
            if CACHE[skey] is False:
                continue
            list_feed = CACHE[skey]
        else:
            # Get the list feed for this spreadsheet
            ss = util.Spreadsheet(spr_client, resources['id'])
            if YEAR not in ss.worksheets:
                print(('Year %s not in spread title: |%s %s|'
                       ) % (YEAR, siteid, spreadtitle))
                CACHE[skey] = False
                continue
            list_feed = ss.worksheets[YEAR].get_list_feed()
            CACHE[skey] = list_feed
        misses = 0
        na = False
        dnc = False
        lookupcol = varconv.get(varname, varname)
        for entry2 in list_feed.entry:
            data = entry2.to_dict()
            if lookupcol not in data:
                na = True
                break
            if data[lookupcol] is None:
                misses += 1
            elif data[lookupcol].lower() == 'did not collect':
                dnc = True

        uri = resources['alternateLink']
        if na:
            newvalue = 'N/A'
        elif dnc:
            newvalue = 'Did not collect'
        elif misses == 0:
            newvalue = 'Complete!'
        else:
            newvalue = '=hyperlink("%s", "Entry")' % (uri,)
        if newvalue != entry.cell.input_value:
            print '--> %s New Value: %s [%s] OLD: %s NEW: %s' % (
                YEAR, siteid, varname, entry.cell.input_value, newvalue)
            entry.cell.input_value = newvalue
            spr_client.update(entry)

for i in range(5, 86):
    do_row(i)
