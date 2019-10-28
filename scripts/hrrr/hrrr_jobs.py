"""What we need to do with HRRR"""
from __future__ import print_function
import sys
import time
import datetime
import subprocess


def main(argv):
    """Stuff"""
    valid = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])
    )
    tstring = valid.strftime("%Y %m %d %H")
    cmds = [
        "python dl_hrrrref.py %s" % (tstring,),
        "python plot_ref.py %s" % (tstring,),
        "python hrrr_ref2raster.py %s" % (tstring,),
    ]
    for cmd in cmds:
        subprocess.call(cmd, shell=True)
        # allow for some time for LDM to move data
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv)
