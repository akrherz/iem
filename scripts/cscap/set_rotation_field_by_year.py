"""
 Go into the various sheets and replace the rotation text with something
 explicit for the year
"""
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient()

xref_plotids = util.get_xref_plotids(spr_client, config)

xref_feed = spr_client.get_list_feed(config.get('cscap', 'xrefrot'), 'od6')

rotations = {}

for entry in xref_feed.entry:
    data = entry.to_dict()

    rotations[data['code']] = data

res = drive.files().list(q="title contains 'Agronomic Data'").execute()

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    siteid = item['title'].split()[0]
    print('Running for site: "%s"...' % (siteid, ))

    plotid_feed = spr_client.get_list_feed(xref_plotids[siteid], 'od6')
    plotids = {}
    for entry2 in plotid_feed.entry:
        row = entry2.to_dict()
        if row['rotation'] is None:
            print('ERROR: Found null rotation for plotids!')
            continue
        plotids[row['plotid']] = row['rotation'].split(
            )[0].replace("[", "").replace("]", "")

    for yr in ['2011', '2012', '2013', '2014', '2015']:
        if yr not in spreadsheet.worksheets:
            continue
        print '--->', item['title'], yr
        worksheet = spreadsheet.worksheets[yr]
        worksheet.get_list_feed()
        for entry in worksheet.list_feed.entry:
            data = entry.to_dict()
            if data['uniqueid'] is None:
                continue
            code = data['rotation'].split(
                )[0].replace("[", "").replace("]", "").replace("ROT", "")
            newval = "ROT%s :: %s" % (code,  rotations["ROT"+code]["y"+yr])
            if plotids[data['plotid']] != code:
                print 'Plot:%s Rotation PlotIdSheet->%s AgSheet->%s' % (
                        data['plotid'], plotids[data['plotid']], code)
            if newval != data['rotation']:
                print 'Plot:%s new:%s old:%s' % (data['plotid'], newval,
                                                 data['rotation'])
                entry.set_value('rotation', newval)
                spr_client.update(entry)
