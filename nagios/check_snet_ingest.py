"""
 Check how much SNET data we have
"""
import sys
import psycopg2


def main():
    """Go Main"""
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
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

    if total > 15:
        print(('OK - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
               ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
        sys.exit(0)
    elif total > 5:
        print(('WARNING - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
               ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
        sys.exit(1)
    else:
        print(('CRITICAL - %s count |kcci=%s;1;3;5 kelo=%s;1;3;5 kimt=%s;1;3;5'
               ) % (total, counts['KCCI'], counts['KELO'], counts['KIMT']))
        sys.exit(2)


if __name__ == '__main__':
    main()
