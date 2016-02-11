"""
"""
import pyiem.cscap_utils as util

config = util.get_config()
ssclient = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

msheet = util.Spreadsheet(ssclient, config['td']['site_measurements'])
msheet.get_worksheets()
sheet = msheet.worksheets['Plot ID']
sheet.get_list_feed()
sites = {}
pis = {}
for entry in sheet.list_feed.entry:
    row = entry.to_dict()
    if row['tileflowandtilenitrate-nyesno'] == 'NO':
        continue
    site = row['siteid']
    d = sites.setdefault(site, [])
    d.append(row['plotid'])
    pis[site] = row['leadpi']

# Use SDC to figure out years
ssheet = util.Spreadsheet(ssclient, config['td']['sdckey'])
ssheet.get_worksheets()
sheet = ssheet.worksheets['Data Collected']
# We can't use the list feed as it corrupts the site IDs
sheet.get_cell_feed()
myrow = None
for i in range(1, sheet.rows + 1):
    if sheet.get_cell_value(i, 1) == 'WAT2':
        myrow = i
        break
years = {}
for col in range(2, sheet.cols + 1):
    site = sheet.get_cell_value(1, col)
    if site not in sites:
        continue
    val = sheet.get_cell_value(myrow, col)
    years[site] = util.translate_years(val)

# Now we dance
DONE = ['STORY', 'SERF_SD', 'CLAY_R', 'SERF_IA', 'SWROC', 'STJOHNS',
        'MUDS2', 'BEAR', "UBWC", 'MAASS']
for site in sites:
    if site in DONE:
        continue
    # Compute the base folder
    foldername = "%s - %s" % (site, pis[site])
    res = util.exponential_backoff(drive.files().list(
        q=("mimeType = 'application/vnd.google-apps.folder' and title = '%s'"
           " and '%s' in parents"
           ) % (foldername, config['td']['syncfolder'])).execute)
    if 'items' not in res:
        print("Folder Fail: %s" % (foldername, ))
        continue
    colfolder = res['items'][0]['id']
    title = "%s Tile Nitrate-N" % (site, )
    body = {'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': colfolder}]
            }
    print("Creating Tile Flow Sheet: %s in %s" % (title, colfolder))
    res = drive.files().insert(body=body).execute()
    spreadkey = res['id']
    row1 = ['Date']
    row2 = ['MM/DD/YYYY']
    for p in sites[site]:
        for v, u in zip(['WAT2 Tile Nitrate-N concentration',
                         'WAT20 Tile Nitrate-N loss'],
                        ['(mg N L-1)', '(kg ha-1)']):
            row1.append("%s %s" % (p, v))
            row2.append(u)
    for yr in years[site]:
        print 'Adding worksheet for year: %s' % (yr, )
        sheet = ssclient.add_worksheet(spreadkey, str(yr), 10, len(row1))
        for colnum in range(len(row1)):
            cell = ssclient.get_cell(spreadkey, sheet.get_worksheet_id(),
                                     1, colnum + 1)
            cell.cell.input_value = row1[colnum]
            ssclient.update(cell)
            cell = ssclient.get_cell(spreadkey, sheet.get_worksheet_id(),
                                     2, colnum + 1)
            cell.cell.input_value = row2[colnum]
            ssclient.update(cell)
    sheet = ssclient.get_worksheet(spreadkey, 'od6')
    ssclient.delete(sheet)
