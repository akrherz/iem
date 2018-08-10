"""Check how much SNET data we have."""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main"""
    pgconn = get_dbconn('iem', user='nobody')
    icursor = pgconn.cursor()
    icursor.execute("""
    SELECT network,
    sum(case when valid > now() - '75 minutes'::interval then 1 else 0 end)
    from current c JOIN stations s on
    (s.iemid = c.iemid)
    WHERE network in ('KCCI','KELO','KIMT') GROUP by network
    """)

    counts = {'KCCI': 0, 'KELO': 0, 'KIMT': 0}
    total = 0
    for row in icursor:
        counts[row[0]] = row[1]
        total += row[1]

    if total > 2:
        print(('OK - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
               ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
        return 0
    elif total > 1:
        print(('WARNING - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
               ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
        return 1
    print(('CRITICAL - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
           ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
    return 2


if __name__ == '__main__':
    sys.exit(main())
