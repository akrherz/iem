'''
 Scrape out the Soil Nitrate data from Google Drive
'''
import sys
import pyiem.cscap_utils as util
import psycopg2
import datetime

YEAR = sys.argv[1]

config = util.get_config()

pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config['database']['host'])
pcursor = pgconn.cursor()

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient(config)

res = drive_client.files(
        ).list(q="title contains 'Soil Nitrate Data'").execute()

DOMAIN = ['SOIL15', 'SOIL22', 'SOIL16', 'SOIL22', 'SOIL25', 'SOIL95',
          'SOIL94', 'SOIL93', 'SOIL92', 'SOIL91', 'SOIL90', 'SOIL89',
          'SOIL88', 'SOIL87', 'SOIL86', 'SOIL85', 'SOIL84', 'SOIL99',
          'SOIL23', 'SOIL76', 'SOIL77', 'SOIL78', 'SOIL79', 'SOIL80',
          'SOIL81', 'SOIL82', 'SOIL83']

# Load up what data we have for this year
current = {}
pcursor.execute("""SELECT site, plotid, varname, depth, subsample, sampledate
 from soil_data WHERE year = %s and varname in %s""", (YEAR,
                                                       tuple(DOMAIN)))
for row in pcursor:
    key = "%s|%s|%s|%s|%s|%s" % row
    current[key] = True

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
        print(('harvest_soil_nitrate: %s[%s] cell(1,1)="%s", skipping'
               ) % (siteid, YEAR, worksheet.get_cell_value(1, 1)))
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

    for row in range(3, worksheet.rows+1):
        plotid = worksheet.get_cell_value(row, 1)
        depth = worksheet.get_cell_value(row, depthcol)
        if plotid is None or depth is None:
            continue
        subsample = "1"
        if locationcol is not None:
            subsample = worksheet.get_cell_value(row, locationcol)

        for col in range(startcol, worksheet.cols+1):
            if worksheet.get_cell_value(1, col) is None:
                print(("h_soil_nitrate site: %s year: %s col: %s is null"
                       ) % (siteid, YEAR, col))
                continue
            colheading = worksheet.get_cell_value(1, col).strip()
            if not colheading.startswith('SOIL'):
                print(('Invalid colheading: %s site: %s year: %s'
                       ) % (colheading, siteid, YEAR))
                continue
            # Attempt to tease out the sampledate
            tokens = colheading.split()
            varname = tokens[0]
            datetest = tokens[1]
            if len(datetest.split("/")) == 3:
                date = datetime.datetime.strptime(datetest, '%m/%d/%Y')
            else:
                if row == 3:
                    print(("h_soil_nitrate %s[%s] unknown sample date %s"
                           ) % (siteid, YEAR, repr(colheading)))
                date = None
            val = worksheet.get_cell_value(row, col, numeric=True)
            if varname not in DOMAIN:
                print(("harvest_soil_nitrate %s[%s] found additional var: %s"
                       ) % (siteid, YEAR, varname))
                DOMAIN.append(varname)
            try:
                pcursor.execute("""
                    INSERT into soil_data(site, plotid, varname, year,
                    depth, value, subsample, sampledate)
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (siteid, plotid, varname, YEAR, depth, val,
                          subsample, date))
            except Exception, exp:
                print(('site: %s year: %s HARVEST_SOIL_NITRATE TRACEBACK'
                       ) % (siteid, YEAR))
                print exp
                print '%s %s %s %s %s %s' % (siteid, plotid, varname, depth,
                                             date, val)
                sys.exit()
            key = ("%s|%s|%s|%s|%s|%s"
                   ) % (siteid, plotid, varname, depth, subsample,
                        date if date is None else date.strftime("%Y-%m-%d"))
            if key in current:
                del(current[key])

for key in current:
    (siteid, plotid, varname, depth, subsample, date) = key.split("|")
    if date != 'None':
        datesql = " and sampledate = '%s' " % (date, )
    else:
        datesql = " and sampledate is null "
    print(('h_soil_nitrate rm %s %s %s %s %s %s %s'
           ) % (YEAR, siteid, plotid, varname, depth, subsample,
                date))
    pcursor.execute("""
        DELETE from soil_data where site = %s and
        plotid = %s and varname = %s and year = %s and depth = %s and
        subsample = %s """ + datesql + """
    """, (siteid, plotid, varname, YEAR, depth, subsample))

    # print "...done"
pcursor.close()
pgconn.commit()
pgconn.close()
