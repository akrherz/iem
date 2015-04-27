"""Remove a column from all Agronomic Sheets!"""
import util
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
drive_client = util.get_driveclient()

res = drive_client.files().list(q="title contains 'Agronomic Data'").execute()

for item in res['items']:
    spreadsheet = util.Spreadsheet(spr_client, item['id'])
    for yr in ["2011", "2012", "2013", "2014", "2015"]:
        spreadsheet.worksheets[yr].del_column("AGR392")
