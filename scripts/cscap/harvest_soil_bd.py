"""Scrape out the Soil Bulk Density and Texture data from Google Drive"""
import pyiem.cscap_utils as util
import sys
import psycopg2

YEAR = sys.argv[1]

config = util.get_config()

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config['database']['host'])
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient(config)

res = drive_client.files().list(q=("title contains '%s'"
                                   ) % (('Soil Bulk Density and '
                                         'Water Retention Data'),)
                                ).execute()

DOMAIN = ['SOIL1', 'SOIL2', 'SOIL29', 'SOIL30', 'SOIL31', 'SOIL32',
          'SOIL33', 'SOIL34', 'SOIL35', 'SOIL39']

# Load up current data, incase we need to do some deleting
current = {}
pcursor.execute("""
    SELECT site, plotid, varname, depth, subsample
    from soil_data WHERE year = %s and varname in %s
    """, (YEAR, tuple(DOMAIN)))
for row in pcursor:
    key = "|".join([str(s) for s in row])
    current[key] = True

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    try:
        spreadsheet = util.Spreadsheet(spr_client, item['id'])
    except Exception, exp:
        print("harvest_soil_bd FAIL: %s\n%s" % (exp, item['title']))
        continue
    spreadsheet.get_worksheets()
    siteid = item['title'].split()[0]
    worksheet = spreadsheet.worksheets.get(YEAR)
    if worksheet is None:
        # print 'Missing Soil BD+WR %s sheet for %s' % (YEAR, siteid)
        continue
    worksheet.get_cell_feed()
    if siteid == 'DPAC':
        pass
    elif (worksheet.get_cell_value(1, 1) != 'plotid' or
            worksheet.get_cell_value(1, 2) != 'depth' or
            worksheet.get_cell_value(1, 3) != 'subsample'):
        print 'FATAL site: %s(%s) bd & wr has bad header 1:%s 2:%s 3:%s' % (
            siteid, YEAR, worksheet.get_cell_value(1, 1),
            worksheet.get_cell_value(1, 2),
            worksheet.get_cell_value(1, 3))
        continue

    for row in range(3, worksheet.rows+1):
        plotid = worksheet.get_cell_value(row, 1)
        if siteid == 'DPAC':
            depth = worksheet.get_cell_value(row, 3)
            # Combine the location value into the subsample
            subsample = '%s%s' % (worksheet.get_cell_value(row, 2),
                                  worksheet.get_cell_value(row, 4))
        else:
            depth = worksheet.get_cell_value(row, 2)
            subsample = worksheet.get_cell_value(row, 3)
        if plotid is None or depth is None:
            continue
        for col in range(4, worksheet.cols+1):
            if worksheet.get_cell_value(1, col) is None:
                # print(("harvest_soil_bd %s(%s) row: %s col: %s is null"
                #       ) % (siteid, YEAR, row, col))
                continue
            varname = worksheet.get_cell_value(1, col).strip().split()[0]
            if varname[:4] != 'SOIL':
                # print 'Invalid varname: %s site: %s year: %s' % (
                #                    worksheet.get_cell_value(1,col).strip(),
                #                    siteid, YEAR)
                continue
            val = worksheet.get_cell_value(row, col, numeric=True)
            try:
                pcursor.execute("""
                    INSERT into soil_data(site, plotid, varname, year,
                    depth, value, subsample)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, depth, val,
                          subsample))
            except Exception, exp:
                print 'HARVEST_SOIL_BD TRACEBACK'
                print exp
                print '%s %s %s %s %s %s' % (siteid, plotid, varname, depth,
                                             val, subsample)
                sys.exit()
            key = "|".join([siteid, plotid, varname, depth, subsample])
            if key in current:
                del(current[key])

for key in current:
    (siteid, plotid, varname, depth, subsample) = key.split("|")
    if varname in DOMAIN:
        print(('harvest_soil_bd rm %s %s %s %s %s %s'
               ) % (YEAR, siteid, plotid, varname, repr(depth),
                    repr(subsample)))
        pcursor.execute("""DELETE from soil_data where site = %s and
        plotid = %s and varname = %s and year = %s and depth = %s and
        subsample = %s""", (siteid, plotid, varname, YEAR, depth,
                            subsample))


pcursor.close()
pgconn.commit()
pgconn.close()
