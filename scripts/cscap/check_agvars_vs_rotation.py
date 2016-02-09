import pyiem.cscap_utils as util
import sys

config = util.get_config()

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient(config)

xref_plotids = util.get_xref_plotids(spr_client, config)

xref_feed = spr_client.get_list_feed(config['cscap']['xrefrot'], 'od6')
rotations = {}
for entry in xref_feed.entry:
    data = entry.to_dict()
    rotations[data['code']] = data

# Build xref of cropmate with variables
cropmates = {}
xref_feed = spr_client.get_list_feed(config['cscap']['xrefrotvars'], 'od6')
for entry in xref_feed.entry:
    data = entry.to_dict()
    res = cropmates.setdefault(data['cropmate'], [])
    res.append(data['variable'].lower())

res = drive.files().list(q="title contains 'Agronomic Data'").execute()

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    print('Processing %s' % (item['title'], ))
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    siteid = item['title'].split()[0]
    plotid_feed = spr_client.get_list_feed(xref_plotids[siteid], 'od6')
    plotids = {}
    for entry2 in plotid_feed.entry:
        row = entry2.to_dict()
        if 'rotation' not in row:
            print 'Invalid headers in plotid sheet for %s\n headers: %s' % (
                                                        item['title'],
                                                        " ".join(row.keys()))
            sys.exit()
        if row['rotation'] is None:
            continue
        plotids[row['plotid']] = row['rotation'].split()[0].replace(
            "[", "").replace("]", "")

    for yr in ['2011', '2012', '2013', '2014', '2015']:
        ylookup = 'y%s' % (yr,)
        if yr not in spreadsheet.worksheets:
            continue
        print('----> %s' % (yr, ))
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            if data['plotid'] is None:
                continue
            rlookup = 'ROT%s' % (plotids[data['plotid']],)
            crop = rotations[rlookup][ylookup]
            dirty = False
            for col in data.keys():
                if col[:3] != 'agr':
                    continue
                # if (col in cropmates.get(crop, []) and data[col] == "."):
                #  print 'Setting to DNC', data['plotid'], crop, col, data[col]
                #    entry.set_value(col, 'did not collect')
                #    dirty = True
                if (col not in cropmates.get(crop, []) and
                        (data[col] is None or
                         data[col].lower() in ['.', 'did not collect'])):
                    print(('    Setting to n/a PlotId: %s Crop: %s '
                           'Col: %s Data: %s'
                           ) % (data['plotid'], crop, col, data[col]))
                    entry.set_value(col, 'n/a')
                    dirty = True
                if data[col] is None:
                    continue
                    # print 'Setting to .', data['plotid'], crop, col
                    # entry.set_value(col, '.')
                    # dirty = True
                elif (col not in cropmates.get(crop, []) and
                      data[col].lower() not in ['.', 'did not collect',
                                                'n/a', 'Not available']):
                    print(("    PlotID: %s crop: %s has data [%s] for %s"
                           ) % (data['plotid'], crop, data[col],
                                col.upper()))
            if dirty:
                print("updating...")
                # spr_client.update(entry)
