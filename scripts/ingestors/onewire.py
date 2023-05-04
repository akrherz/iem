"""Onewire ingest."""
import datetime
import os
import time

os.environ["TZ"] = "CST6CDT"


def main():
    """Go Main Go"""
    with open("runner.pid", "w") as fh:
        fh.write("%s" % (os.getpid(),))

    while 1:
        _si, so = os.popen4('./digitemp -q -a -s /dev/ttyS0 -o"%s %.2F"')
        d = so.readlines()
        data = {}
        for ll in d:
            t = ll.split()
            try:
                data[int(t[0])] = t[1]
            except Exception:
                print(ll)
        if len(data) > 3:
            now = datetime.datetime.now()
            fp = "ot0003_%s.dat" % (now.strftime("%Y%m%d%H%M"),)
            with open(fp, "w") as fh:
                fh.write(
                    "104,%s,%s, %s, %s, %s,11.34\n"
                    % (
                        now.strftime("%Y,%j,%H%M"),
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                    )
                )
            os.system("pqinsert %s" % (fp,))
            os.remove(fp)
        time.sleep(56)


if __name__ == "__main__":
    main()
