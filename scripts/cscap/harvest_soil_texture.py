'''
 Scrape out the Soil Texture data from Google Drive
'''
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

allowed_depths = ['0 - 10', '10 - 20', '20 - 40', '40 - 60']

drive_client = util.get_driveclient(config)

DOMAIN = ['SOIL26', 'SOIL27', 'SOIL28', 'SOIL6',
          'SOIL11', 'SOIL12', 'SOIL13', 'SOIL14']

# Load up current data
current = {}
pcursor.execute("""SELECT site, plotid, varname, depth, subsample, value
    from soil_data WHERE year = %s and varname in %s
    """, (YEAR, tuple(DOMAIN)))
for row in pcursor:
    key = "%s|%s|%s|%s|%s" % row[:5]
    current[key] = row[4]

res = drive_client.files(
        ).list(q="title contains 'Soil Texture Data'").execute()

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    if YEAR not in spreadsheet.worksheets:
        # print(("Missing %s from %s") % (YEAR, spreadsheet.title))
        continue
    worksheet = spreadsheet.worksheets[YEAR]
    worksheet.get_cell_feed()
    siteid = item['title'].split()[0]
    # print 'Processing %s Soil Texture Year %s' % (siteid, YEAR)
    if (worksheet.get_cell_value(1, 1) != 'plotid' or
            worksheet.get_cell_value(1, 2) != 'depth'):
        print(('harvest_soil_texture %s[%s] headers: "%s","%s", skipping'
               ) % (siteid, YEAR, worksheet.get_cell_value(1, 1),
                    worksheet.get_cell_value(1, 2)))
        continue

    for row in range(4, worksheet.rows+1):
        plotid = worksheet.get_cell_value(row, 1)
        depth = worksheet.get_cell_value(row, 2)
        # if depth not in allowed_depths:
        #    print 'site: %s year: %s has illegal depth: %s' % (siteid, YEAR,
        #                                                       depth)
        #    continue
        if plotid is None or depth is None:
            continue
        subsample = "1"
        for col in range(3, worksheet.cols+1):
            if worksheet.get_cell_value(1, col) is None:
                print(('harvest_soil_texture Year: %s Site: %s Col: %s is null'
                       ) % (YEAR, siteid, col))
                continue
            varname = worksheet.get_cell_value(1, col).strip().split()[0]
            val = worksheet.get_cell_value(row, col, numeric=True)
            if varname == 'subsample':
                subsample = "%.0f" % (float(val), )
                continue
            elif varname[:4] != 'SOIL':
                print(('Invalid varname: %s site: %s year: %s'
                       ) % (worksheet.get_cell_value(1, col).strip(),
                            siteid, YEAR))
                continue
            # if subsample != "1":
            #    continue
            try:
                pcursor.execute("""
                    INSERT into soil_data(site, plotid, varname, year,
                    depth, value, subsample)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, depth, val,
                          subsample))
            except Exception, exp:
                print 'HARVEST_SOIL_TEXTURE TRACEBACK'
                print exp
                print '%s %s %s %s %s' % (siteid, plotid, varname, depth, val,
                                          subsample)
                sys.exit()
            key = "%s|%s|%s|%s" % (plotid, varname, depth, subsample)
            if key in current:
                del(current[key])

for key in current:
    (siteid, plotid, varname, depth, subsample) = key.split("|")
    if varname in DOMAIN:
        print(('harvest_soil_texture rm %s %s %s %s %s %s %s'
               ) % (YEAR, siteid, plotid, varname, depth, subsample,
                    current[key]))
        pcursor.execute("""DELETE from soil_data where site = %s and
        plotid = %s and varname = %s and year = %s and depth = %s and
        subsample = %s""", (siteid, plotid, varname, YEAR, depth,
                            subsample))


pcursor.close()
pgconn.commit()
pgconn.close()
