"""Create an analysis of LSR snowfall reports"""
import tempfile
import os
import subprocess

import requests


def main():
    """Go Main Go."""
    url = (
        "http://iem.local/plotting/auto/plot/207/t:state::csector:IA"
        "::p:both::hours:12.png"
    )
    res = requests.get(url, timeout=30)
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(res.content)
    tmpfd.close()
    pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
    subprocess.call("pqinsert -p '%s' %s" % (pqstr, tmpfd.name), shell=True)
    os.unlink(tmpfd.name)

    # -----------------
    url = (
        "http://iem.local/plotting/auto/plot/207/t:state::csector:midwest"
        "::p:contour::hours:12.png"
    )
    res = requests.get(url, timeout=30)
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(res.content)
    tmpfd.close()
    pqstr = "plot c 000000000000 mw_lsr_snowfall.png bogus png"
    subprocess.call("pqinsert -p '%s' %s" % (pqstr, tmpfd.name), shell=True)
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
