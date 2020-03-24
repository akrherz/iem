"""Process what our weblog has.

Run every minute, sigh.
"""
import sys
import subprocess

import psycopg2


def logic(counts, family):
    """Should we or should we not, that is the question."""
    exe = "iptables" if family == 4 else "ip6tables"
    for addr, hits in counts.items():
        if len(hits) < 30:
            continue
        cmd = "%s -A INPUT -s %s -j DROP" % (exe, addr)
        print(cmd)
        for hit in hits[:10]:
            print("%s uri:|%s| ref:|%s|" % (hit[0], hit[2], hit[3]))
        print()
        subprocess.call(cmd, shell=True)


def main(argv):
    """Go Main Go."""
    family = int(argv[1])  # either 4 or 6
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
        WHERE http_status = 404 and family(client_addr) = %s
        ORDER by valid ASC
    """,
        (family,),
    )
    valid = None
    counts = {}
    for row in cursor:
        d = counts.setdefault(row[1], [])
        d.append(row)
        valid = row[0]

    if valid is None:
        return
    cursor.execute(
        """
        DELETE from weblog where valid <= %s and family(client_addr) = %s
        """,
        (valid, family),
    )
    cursor.close()
    pgconn.commit()
    logic(counts, family)


if __name__ == "__main__":
    main(sys.argv)
