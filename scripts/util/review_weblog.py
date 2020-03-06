"""Process what our weblog has.

Run every minute, sigh.
"""
import re
import subprocess

import psycopg2

IPV4 = re.compile(r"^\d+\.\d+\.\d+\.\d+$")


def logic(counts):
    """Should we or should we not, that is the question."""
    for addr, hits in counts.items():
        if len(hits) < 30:
            continue
        cmd = "iptables -A INPUT -s %s -j DROP" % (addr,)
        print(cmd)
        for hit in hits[:10]:
            print("%s uri:|%s| ref:|%s|" % (hit[0], hit[2], hit[3]))
        print()
        subprocess.call(cmd, shell=True)


def main():
    """Go Main Go."""
    pgconn = psycopg2.connect(
        database="mesosite",
        host="iemdb-mesosite.local",
        user="nobody",
        connect_timeout=5,
        gssencmode="disable",
    )
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT valid, client_addr, uri, referer from weblog
        WHERE http_status = 404 ORDER by valid ASC
    """
    )
    valid = None
    counts = {}
    for row in cursor:
        m = IPV4.match(row[1])
        if not m:
            continue
        d = counts.setdefault(row[1], [])
        d.append(row)
        valid = row[0]

    if valid is None:
        return
    cursor.execute("""DELETE from weblog where valid <= %s""", (valid,))
    cursor.close()
    pgconn.commit()
    logic(counts)


if __name__ == "__main__":
    main()
