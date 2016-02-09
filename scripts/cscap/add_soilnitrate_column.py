"""
Add a column to the soil nitrate sheets
"""
import pyiem.cscap_utils as util

config = util.get_config()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient()

res = drive_client.files().list(
        q="title contains 'Soil Nitrate Data'").execute()

newcols = [
           ['SOIL22 Soil Ammonium (Optional)', 'mg per kg soil'],
           ]

for item in res['items']:
    feed2 = spr_client.GetWorksheets(item['id'])
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        print 'Processing %s WRK: %s Title: %s' % (item['title'],
                                                   worksheet,
                                                   entry2.title.text),
        feed3 = spr_client.get_list_feed(item['id'], worksheet)
        row = feed3.entry[0]
        data = row.to_dict()

        plusone = int(entry2.col_count.text) + 1
        entry2.col_count.text = str(plusone)
        spr_client.update(entry2)

        # Add a column?
        for i in range(len(newcols)):
            cell = spr_client.get_cell(item['id'], worksheet, 1, plusone-i)
            cell.cell.input_value = newcols[i][0]
            spr_client.update(cell)

            cell = spr_client.get_cell(item['id'], worksheet, 2, plusone-i)
            cell.cell.input_value = newcols[i][1]
            spr_client.update(cell)

        print ' ... updated'
        # sys.exit()
