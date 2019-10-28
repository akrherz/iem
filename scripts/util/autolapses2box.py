"""Send autolapse tar files to box for archival.

Run from RUN_MIDNIGHT.sh for the previous date"""
import datetime
import os
import stat
import glob

from pyiem.box_utils import sendfiles2box


def main():
    """Run for the previous date, please"""
    valid = datetime.date.today() - datetime.timedelta(days=1)
    now = datetime.datetime.now()
    os.chdir("/mesonet/share/lapses/auto")
    localfns = []
    for tarfilename in glob.glob("*frames.tar"):
        # Make sure this file was generated yesterday and not old.
        mtime = os.stat(tarfilename)[stat.ST_MTIME]
        age = float(now.strftime("%s")) - mtime
        if age > 86400.0:
            continue
        localfns.append(tarfilename)
    if not localfns:
        print("autolapses2box found no files within the past day?")
        return

    remotepath = valid.strftime("/iemwebcams/auto/%Y/%m/%d")
    res = sendfiles2box(remotepath, localfns)
    for sid, fn in zip(res, localfns):
        if sid is None:
            print("failed to upload %s" % (fn,))


if __name__ == "__main__":
    main()
