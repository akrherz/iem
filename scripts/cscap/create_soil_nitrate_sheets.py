import gdata.spreadsheets.data
import pyiem.cscap_utils as util

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

meta_feed = spr_client.get_list_feed(config['cscap']['metamaster'], 'od6')
sdc_feed = spr_client.get_list_feed(config['cscap']['sdckey'], 'od6')
treat_feed = spr_client.get_list_feed(config['cscap']['treatkey'], 'od6')

sdc_data, sdc_names = util.build_sdc(sdc_feed)

NOTDONE = ['VICMS', ]

for entry in meta_feed.entry:
    data = entry.to_dict()
    sitekey = data.get('uniqueid').lower()
    if sitekey.upper() not in NOTDONE:
        print 'skip', sitekey
        continue
    soil15 = 'SOIL15' in sdc_data["2013"][sitekey]
    soil16 = 'SOIL16' in sdc_data["2013"][sitekey]
    soil23 = 'SOIL23' in sdc_data["2013"][sitekey]
    if not soil15 and not soil16 and not soil23:
        print 'Skipping', sitekey, 'as they have no entries for SOIL15,16,23'
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
            plots.append(cols.get('plotid'))

    if len(plots) == 0:
        print 'No plot IDs found for: %s %s' % (leadpi, sitekey.upper())
        continue

    # Figure out our columns
    columns = ['plotid', 'depth', 'soil nitrate fall sampling']
    units = ['', 'cm', 'mg per kg soil', 'mg per kg soil', 'mg per kg soil']
    if soil15:
        columns.append('SOIL15 soil nitrate spring sampling')
    if soil16:
        columns.append('SOIL16 soil nitrate summer sampling')
    if soil23:
        columns.append('SOIL23 soil nitrate fall sampling')
    depths = ['0 - 30', '30 - 60', '60 - 90']

    # Figure out how many
    rows = []
    # Units row
    entry = gdata.spreadsheets.data.ListEntry()
    for i in range(len(columns)):
        entry.set_value(columns[i].replace(" ", ''), units[i])
    rows.append(entry)
    for plot in plots:
        for depth in depths:
            entry = gdata.spreadsheets.data.ListEntry()
            for col in columns:
                entry.set_value(col.replace(" ", ''), '')
            entry.set_value('depth', depth)
            entry.set_value('plotid', plot)
            rows.append(entry)

    # Okay, now we are ready to create a spreadsheet
    title = '%s %s Soil Nitrate Data' % (sitekey.upper(), leadpi)
    print 'Adding %s Rows: %s' % (title, len(rows))
    body = {'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': colfolder}]
            }
    res = drive.files().insert(body=body).execute()
    spreadkey = res['id']
    for yr in ['2011', '2012', '2013', '2014', '2015']:
        print 'Adding worksheet for year: %s' % (yr,)
        sheet = spr_client.add_worksheet(spreadkey, yr, 10, len(columns))
        for colnum in range(len(columns)):
            cell = spr_client.get_cell(spreadkey, sheet.get_worksheet_id(),
                                       1, colnum+1)
            cell.cell.input_value = columns[colnum]
            spr_client.update(cell)
        for row in rows:
            spr_client.add_list_entry(row, spreadkey, sheet.get_worksheet_id())
    sheet = spr_client.get_worksheet(spreadkey, 'od6')
    spr_client.delete(sheet)
