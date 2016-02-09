"""
 Something that will create dataspreadsheets based on entries in the table
"""
import gdata.spreadsheets.data
import copy
import pyiem.cscap_utils as util

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

meta_feed = spr_client.get_list_feed(config['cscap']['metamaster'], 'od6')
sdc_feed = spr_client.get_list_feed(config['cscap']['sdckey'], 'od6')
treat_feed = spr_client.get_list_feed(config['cscap']['treatkey'], 'od6')

treatments, treatment_names = util.build_treatments(treat_feed)
sdc, sdc_names = util.build_sdc(sdc_feed)

"""
Okay, we are cross product TIL x ROT x DWN x NIT
"""

baseheaders = ['UniqueID', 'Rep', 'Tillage', 'Rotation', 'Drainage',
               'Nitrogen', 'Landscape', 'PlotID', 'ROW', 'COLUMN']
basecolumns = {'A': 'UniqueID', 'B': 'Rep', 'C': 'Tillage', 'D': 'Rotation',
               'E': 'Drainage', 'F': 'Nitrogen', 'G': 'Landscape',
               'H': 'Plot ID', 'I': 'ROW', 'J': 'COLUMN'}

letters = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
           'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH',
           'AI', 'AJ', 'AK', 'AL']

TODO = ['vicms']

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey not in TODO:
        print 'skip', sitekey
        continue
    # This is the folder where synced data is stored
    colfolder = data.get('colfolder')
    leadpi = data.get('leadpi')

    # Lets go find the Plot Identifiers Table
    keyspread = data.get('keyspread')
    # loop over rows
    plots = []
    feed = spr_client.get_list_feed(keyspread, 'od6')
    for feed_entry in feed.entry:
        cols = feed_entry.to_dict()
        if cols.get('plotid', '') not in ['', None]:
            plots.append(cols)

    if len(plots) == 0:
        print 'No plot IDs found for: %s %s' % (leadpi, sitekey.upper())
        continue

    # Figure out our columns
    columns = basecolumns.copy()
    headers = copy.deepcopy(baseheaders)
    i = 0
    datavars = []
    for yr in ['2011', '2012', '2013', '2014', '2015']:
        for datavar in sdc[yr][sitekey]:
            if datavar.find("AGR") > -1 and datavar not in datavars:
                hid = datavar
                columns[letters[i]] = hid
                datavars.append(hid)
                headers.append(hid)
                i += 1

    if len(datavars) == 0:
        print 'NO AGR DATA! %s' % (sitekey,)
        continue

    # Figure out how many
    rows = []
    # Do row 2
    entry = gdata.spreadsheets.data.ListEntry()
    for dv in datavars:
        hid = '%s' % (sdc_names[dv]['name'], )
        entry.set_value(dv.lower(), hid)
    for col in plots[0].keys():
        entry.set_value(col, '')
    rows.append(entry)
    # Do row 3
    entry = gdata.spreadsheets.data.ListEntry()
    for dv in datavars:
        hid = '%s' % (sdc_names[dv]['units'],)
        entry.set_value(dv.lower(), hid)
    for col in plots[0].keys():
        entry.set_value(col, '')
    rows.append(entry)
    for plot in plots:
        entry = gdata.spreadsheets.data.ListEntry()
        for dv in datavars:
            entry.set_value(dv.lower(), '')
        for col in plot.keys():
            entry.set_value(col, plot[col])
        rows.append(entry)

    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Agronomic Data' % (sitekey.upper(), leadpi)
    print 'Adding: %s ROWS: %s' % (title, len(rows))
    body = {'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': colfolder}]
            }
    res = drive.files().insert(body=body).execute()
    spreadkey = res['id']
    for yr in ['2011', '2012', '2013', '2014', '2015']:
        print 'Adding worksheet for year: %s' % (yr,)
        sheet = spr_client.add_worksheet(spreadkey, yr, 10, len(columns))
        for colnum in range(len(headers)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),
                                       1, colnum+1)
            cell.cell.input_value = headers[colnum]
            spr_client.update(cell)
        for row in rows:
            spr_client.add_list_entry(row, spreadkey, sheet.get_worksheet_id())
    sheet = spr_client.get_worksheet(spreadkey, 'od6')
    spr_client.delete(sheet)
