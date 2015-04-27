'''
 Scrape out the Soil Nitrate data from Google Drive
'''
import util
import sys
import ConfigParser
import psycopg2

YEAR = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config.get('database', 'host'))
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient()

res = drive_client.files(
        ).list(q="title contains 'Soil Nitrate Data'").execute()

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    worksheet = spreadsheet.worksheets.get(YEAR)
    if worksheet is None:
        # print("Missing Year: %s from %s" % (YEAR, spreadsheet.title))
        continue
    worksheet.get_cell_feed()
    siteid = item['title'].split()[0]
    # print 'Processing %s Soil Nitrate Year %s' % (siteid, YEAR),
    if worksheet.get_cell_value(1, 1) != 'plotid':
        print 'FATAL site: %s soil nitrate has corrupt headers' % (siteid,)
        continue
    startcol = 3
    if worksheet.get_cell_value(1, 2) == 'depth':
        depthcol = 2
    elif worksheet.get_cell_value(1, 3) == 'depth':
        depthcol = 3
        startcol = 4
    if worksheet.get_cell_value(1, 2) == 'location':
        locationcol = 2
    else:
        locationcol = None

    # Load up current data
    current = {}
    pcursor.execute("""SELECT plotid, varname, depth, subsample
    from soil_data WHERE site = %s and year = %s""", (siteid, YEAR))
    for row in pcursor:
        key = "%s|%s|%s|%s" % row
        current[key] = True
    found_vars = []

    for row in range(3, worksheet.rows+1):
        plotid = worksheet.get_cell_value(row, 1)
        depth = worksheet.get_cell_value(row, depthcol)
        if plotid is None or depth is None:
            continue
        subsample = "1"
        if locationcol is not None:
            subsample = worksheet.get_cell_value(row, locationcol)

        for col in range(startcol, worksheet.cols+1):
            varname = worksheet.get_cell_value(1, col).strip().split()[0]
            if varname[:4] != 'SOIL':
                print(('Invalid varname: %s site: %s year: %s'
                       ) % (worksheet.get_cell_value(1, col).strip(),
                            siteid, YEAR))
                continue
            val = worksheet.get_cell_value(row, col)
            if varname not in found_vars:
                found_vars.append(varname)
            try:
                pcursor.execute("""
                    INSERT into soil_data(site, plotid, varname, year,
                    depth, value, subsample)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, depth, val,
                          subsample))
            except Exception, exp:
                print(('site: %s year: %s HARVEST_SOIL_NITRATE TRACEBACK'
                       ) % (siteid, YEAR))
                print exp
                print '%s %s %s %s %s' % (siteid, plotid, varname, depth, val)
                sys.exit()
            key = "%s|%s|%s|%s" % (plotid, varname, depth, subsample)
            if key in current:
                del(current[key])

    for key in current:
        (plotid, varname, depth, subsample) = key.split("|")
        if varname in found_vars:
            print(('harvest_soil_nitrate rm %s %s %s %s %s %s'
                   ) % (YEAR, siteid, plotid, varname, depth, subsample))
            pcursor.execute("""DELETE from soil_data where site = %s and
            plotid = %s and varname = %s and year = %s and depth = %s and
            subsample = %s""", (siteid, plotid, varname, YEAR, depth,
                                subsample))

    # print "...done"
pcursor.close()
pgconn.commit()
pgconn.close()
