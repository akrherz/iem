"""
"""
import pyiem.cscap_utils as util


def has_or_create_worksheet(ssclient, sheet, title, rows, cols):
    sheet.get_worksheets()
    if title not in sheet.worksheets:
        print 'Adding worksheet with title: %s' % (title, )
        ssclient.add_worksheet(sheet.id, title, rows, cols)
        sheet.get_worksheets()
    return sheet.worksheets[title]


def has_or_create_sheet(drive, colfolder, title):
    """ Create or find this sheet!"""
    res = util.exponential_backoff(drive.files().list(
        q=("mimeType = 'application/vnd.google-apps.spreadsheet' "
           "and title = '%s' and '%s' in parents"
           ) % (title, colfolder)).execute)
    if len(res['items']) == 0:
        body = {'title': title,
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [{'id': colfolder}]
                }
        print("Creating Tile Flow Sheet: %s in %s" % (title, colfolder))
        res = drive.files().insert(body=body).execute()
        return res['id']
    return res['items'][0]['id']

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
    d.append(row['waterqualityid'])
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
NOT_DONE = ['BATH_A', 'TIDE_NEW', 'TIDE_OLD']
for site in sites:
    if site not in NOT_DONE:
        continue
    print("---- Processing: %s -----" % (site, ))
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
    spreadkey = has_or_create_sheet(drive, colfolder, title)
    spreadsheet = util.Spreadsheet(ssclient, spreadkey)
    row1 = ['Date']
    row2 = ['MM/DD/YYYY']
    for p in sites[site]:
        for v, u in zip(['WAT2 Tile Nitrate-N concentration',
                         'WAT20 Tile Nitrate-N loss'],
                        ['(mg N L-1)', '(kg ha-1)']):
            row1.append("%s %s" % (p, v))
            row2.append(u)
    for yr in years[site]:
        worksheet = has_or_create_worksheet(ssclient, spreadsheet, str(yr), 10,
                                            len(row1))
        worksheet.get_cell_feed()
        if worksheet.cols != len(row1):
            print("len mismatch worksheet.cols: %s, new: %s" % (worksheet.cols,
                                                                len(row1)))
        for colnum in range(len(row1)):
            if colnum >= worksheet.cols:
                print("Expanding %s[%s] by one column" % (title, yr))
                worksheet.expand_cols(1)
            cell = worksheet.get_cell_entry(1, colnum + 1)
            if cell.cell.input_value != row1[colnum]:
                cell.cell.input_value = row1[colnum]
                util.exponential_backoff(ssclient.update, cell)
            cell = worksheet.get_cell_entry(2, colnum + 1)
            if cell.cell.input_value != row2[colnum]:
                cell.cell.input_value = row2[colnum]
                util.exponential_backoff(ssclient.update, cell)
        delcols = []
        for colnum in range(len(row1), worksheet.cols):
            delcols.append(worksheet.get_cell_value(1, colnum+1))
        if len(delcols) > 0:
            for delcol in delcols:
                print("   deleting column %s %s" % (yr, delcol))
                worksheet.del_column(delcol)
    if 'sheet1' in spreadsheet.worksheets:
        sheet = ssclient.get_worksheet(spreadkey, 'od6')
        ssclient.delete(sheet)
