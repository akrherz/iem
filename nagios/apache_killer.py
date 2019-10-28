"""Script that kills apache processes that are likely in-error.

This appears to be due to some proxy / mod-wsgi issue that I am not clever
enough to fix.
"""
from __future__ import print_function

import psutil

# CPU time in seconds to kill
THRESHOLD = 86400


def main():
    """Go Main"""
    for proc in psutil.process_iter():
        if proc.username() != "apache":
            continue
        vals = proc.cpu_times()
        if vals[0] > THRESHOLD:
            # print("%s %s" % (proc.pid, vals[0]))
            proc.send_signal(9)


if __name__ == "__main__":
    main()
