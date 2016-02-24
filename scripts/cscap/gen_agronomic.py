"""Create Agronomic Sheets"""
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
        print("Creating Sheet: %s in %s" % (title, colfolder))
        res = drive.files().insert(body=body).execute()
        return res['id']
    return res['items'][0]['id']


config = util.get_config()
spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

sites = {}
pis = {}
spreadsheet = util.Spreadsheet(spr_client, config['td']['site_measurements'])
spreadsheet.get_worksheets()
worksheet = spreadsheet.worksheets['Agro Plot ID']
worksheet.get_list_feed()
for entry in worksheet.list_feed.entry:
    data = entry.to_dict()
    siteid = data['siteid']
    pis[siteid] = data['leadpi']
    plotid = data['plotid']
    d = sites.setdefault(siteid, {})
    d[plotid] = {}
    for year in range(1996, 2019):
        opt = data["y%s" % (year, )]
        if opt is None or opt == "" or opt == "n/a":
            continue
        d[plotid][str(year)] = {'corn': (opt.find("C") > -1),
                                'soy': (opt.find('S') > -1),
                                'wheat': (opt.find('W') > -1)}
NOT_DONE = ['BATH_A', 'TIDE_NEW', 'TIDE_OLD']
for site in sites:
    if site not in NOT_DONE:
        continue
    foldername = "%s - %s" % (site, pis[site])
    print("Searching for foldername |%s|" % (foldername, ))
    res = util.exponential_backoff(drive.files().list(
        q=("mimeType = 'application/vnd.google-apps.folder' and title = '%s'"
           " and '%s' in parents"
           ) % (foldername, config['td']['syncfolder'])).execute)
    if res is None or 'items' not in res:
        print("Folder Fail: %s" % (foldername, ))
        continue
    colfolder = res['items'][0]['id']
    title = "%s Crop Yield Data" % (site, )
    spreadkey = has_or_create_sheet(drive, colfolder, title)
    spreadsheet = util.Spreadsheet(spr_client, spreadkey)
    years = []
    for plotid in sites[site]:
        for year in sites[site][plotid]:
            if year not in years:
                years.append(year)
    years.sort()
    if len(years) == 0:
        continue
    for yr in years:
        worksheet = has_or_create_worksheet(spr_client, spreadsheet, str(yr),
                                            10, 2)
        corn = False
        soy = False
        wheat = False
        for plotid in sites[site]:
            if yr not in sites[site][plotid]:
                continue
            if sites[site][plotid][yr]['corn']:
                corn = True
            if sites[site][plotid][yr]['soy']:
                soy = True
            if sites[site][plotid][yr]['wheat']:
                wheat = True
        row1 = ['Plot ID', ]
        row2 = ['', ]
        if corn:
            row1.append('AGR17 Corn grain yield at 15.5% MB')
            row2.append('kg ha-1')
            row1.append('AGR18 Corn grain moisture')
            row2.append('%')
        if soy:
            row1.append('AGR19 Soybean grain yield at 13.0% MB')
            row2.append('kg ha-1')
            row1.append('AGR20 Soybean grain moisture')
            row2.append('%')
        if wheat:
            row1.append('AGR21 Wheat grain yield at 13.5% MB')
            row2.append('kg ha-1')
            row1.append('AGR22 Wheat grain moisture')
            row2.append('%')
        if len(row1) == 1:
            continue
        for colnum in range(len(row1)):
            if colnum >= worksheet.cols:
                print("Expanding %s[%s] by one column" % (title, yr))
                worksheet.expand_cols(1)
            cell = spr_client.get_cell(spreadkey, worksheet.id,
                                       1, colnum + 1)
            if cell.cell.input_value != row1[colnum]:
                cell.cell.input_value = row1[colnum]
                util.exponential_backoff(spr_client.update, cell)
            cell = spr_client.get_cell(spreadkey, worksheet.id,
                                       2, colnum + 1)
            if cell.cell.input_value != row2[colnum]:
                cell.cell.input_value = row2[colnum]
                util.exponential_backoff(spr_client.update, cell)
        plotids = sites[site].keys()
        plotids.sort()
        for i, plotid in enumerate(plotids):
            if (i + 2) >= worksheet.rows:
                print("Expanding %s[%s] by one row" % (title, yr))
                worksheet.expand_rows(1)
            cell = spr_client.get_cell(spreadkey, worksheet.id,
                                       i+3, 1)
            if cell.cell.input_value != plotid:
                cell.cell.input_value = plotid
                util.exponential_backoff(spr_client.update, cell)
    if 'Sheet1' in spreadsheet.worksheets:
        sheet = spr_client.get_worksheet(spreadkey, 'od6')
        spr_client.delete(sheet)
