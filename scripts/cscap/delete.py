import pyiem.cscap_utils as util
import sys
config = util.get_config()
drive = util.get_driveclient(config)

print drive.files().delete(fileId=sys.argv[1]).execute()
