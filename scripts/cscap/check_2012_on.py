"""
  Look at the Agronomic Sheets and see if the number of rows match between
  2011 and the rest of the years
"""
import ConfigParser
import util  # @UnresolvedImport

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
drive = util.get_driveclient()

res = drive.files().list(q="title contains 'Agronomic Data'").execute()

for item in res['items']:
    if item['mimeType'] != 'application/vnd.google-apps.spreadsheet':
        continue
    print '------------>', item['title']
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    spreadsheet.get_worksheets()
    if '2011' not in spreadsheet.worksheets:
        print('ERROR: Does not have 2011 sheet')
        continue
    worksheet = spreadsheet.worksheets['2011']
    rows = worksheet.rows
    for yr in ['2012', '2013', '2014', '2015']:
        worksheet = spreadsheet.worksheets[yr]
        if rows != worksheet.rows:
            print('    Year: %s has row count: %s , 2011 has: %s'
                  ) % (yr, worksheet.rows, rows)
