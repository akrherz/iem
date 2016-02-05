"""
Interogate the spreadsheets and see if the units values have been modified
"""
import util  # @UnresolvedImport
import ConfigParser

types = {'Agronomic Data': 3,
         'Soil Nitrate Data': 2,
         'Soil Texture Data': 3,
         'Soil Bulk Density and Water Retention Data': 2}

drive = util.get_driveclient()
smartsheet = util.get_ssclient()
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')
spr_client = util.get_spreadsheet_client(config)

# Build the XREF of IDs to units
xref = {}
sheet = smartsheet.Sheets.get_sheet('3480487181215620', page_size=1000)
titles = []
for col in sheet.columns:
    titles.append(col.title)
cidx = titles.index('Code (Column Heading)')
uidx = titles.index('Units')

for row in sheet.rows:
    codeval = row.cells[cidx].value
    if codeval.startswith("SOIL") or codeval.startswith("AGR"):
        units = row.cells[uidx].value
        xref[codeval] = units.lower() if units != 'unitless' else None

skip = ['COLUMN', 'ROW', 'PlotID', 'Tillage', 'Rotation', 'Nitrogen',
        'UniqueID', 'Rep', 'Drainage', 'Landscape', 'uniqueid', 'depth',
        'subsample', 'plotid', 'UniqueId', 'NOTES', 'Herbicide',
        'location', 'Treatment', 'Location']
for title in types:
    res = drive.files().list(q="title contains '%s'" % (title,)).execute()
    for item in res['items']:
        if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
            continue
        siteid = item['title'].split()[0]
        spreadsheet = util.Spreadsheet(spr_client, item['id'])
        spreadsheet.get_worksheets()
        for year in spreadsheet.worksheets:
            worksheet = spreadsheet.worksheets[year]
            worksheet.get_cell_feed()
            for col in range(1, worksheet.cols+1):
                varname = worksheet.get_cell_value(1, col)
                if varname is None:
                    continue
                varname = varname.split()[0]
                if varname in skip:
                    continue
                if xref.get(varname, 1) is None:
                    continue
                units = worksheet.get_cell_value(types[title], col)
                if units is None:
                    print(("%s %s %s %s has no units, should be %s"
                           ) % (siteid, year, title, varname,
                                xref.get(varname)))
                    continue
                units = units.lower().strip()
                if varname not in xref:
                    print(("Unknown varname: |%s| in %s %s [%s]"
                           ) % (varname, siteid, title, year))
                    continue
                if xref[varname] != units:
                    print(("%s %s[%s] -> %s|%s| uses |%s|"
                           ) % (siteid, title, year, varname,
                                xref[varname], units))
