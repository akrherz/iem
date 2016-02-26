import datetime
import pytz
import pyiem.cscap_utils as util

config = util.get_config()

FOLDERS = {}

drive = util.get_driveclient(config, "cscap")
sprclient = util.get_spreadsheet_client(config)

print sprclient.GetWorksheets('1UeEJ0rTQaP0H2nidUDaNVu9D5Mw26BuaHInkAJnF6ms')
