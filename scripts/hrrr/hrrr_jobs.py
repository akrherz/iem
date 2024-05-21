"""What we need to do with HRRR"""

import datetime
import subprocess
import sys
import time


def main(argv):
    """Stuff"""
    valid = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])
    )
    tstring = valid.strftime("%Y %m %d %H")
    extra = " --is-realtime" if argv[5] == "RT" else ""
    cmds = [
        f"python dl_hrrrref.py {tstring}",
        f"python plot_ref.py --valid={valid:%Y-%m-%dT%H:%M:%S}{extra}",
        f"python hrrr_ref2raster.py {tstring} {argv[5]}",
    ]
    for cmd in cmds:
        subprocess.call(cmd.split())
        # allow for some time for LDM to move data
        time.sleep(120)


if __name__ == "__main__":
    main(sys.argv)
