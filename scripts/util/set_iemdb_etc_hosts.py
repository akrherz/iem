"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry."""
import sys
import tempfile
import os

METVM4, METVM6, METVM2 = range(3)
IPS = "172.16.170.1 172.16.172.1 172.16.174.1".split()
LOOKUP = {
    "": IPS[METVM4],
    "-afos": IPS[METVM4],
    "-asos": IPS[METVM4],
    "-asos1min": IPS[METVM4],
    "-awos": IPS[METVM6],
    "-coop": IPS[METVM2],
    "-frost": IPS[METVM4],
    "-hads": IPS[METVM2],
    "-hml": IPS[METVM6],
    "-id3b": IPS[METVM4],
    "-idep": IPS[METVM4],
    "-iem": IPS[METVM4],
    "-iemre": IPS[METVM2],
    "-isuag": IPS[METVM4],
    "-kcci": IPS[METVM4],
    "-mec": IPS[METVM6],
    "-mesonet": IPS[METVM4],
    "-mesosite": IPS[METVM4],
    "-mos": IPS[METVM6],
    "-nc1018": IPS[METVM4],
    "-nldn": IPS[METVM2],
    "-nwx": IPS[METVM4],
    "-openfire": IPS[METVM6],
    "-other": IPS[METVM4],
    "-portfolio": IPS[METVM4],
    "-postgis": IPS[METVM2],
    "-radar": IPS[METVM2],
    "-raob": IPS[METVM2],
    "-rtstats": IPS[METVM4],
    "-rwis": IPS[METVM4],
    "-scada": IPS[METVM4],
    "-scan": IPS[METVM4],
    "-smos": IPS[METVM2],
    "-snet": IPS[METVM6],
    "-squaw": IPS[METVM4],
    "-sustainablecorn": IPS[METVM4],
    "-talltowers": IPS[METVM2],
    "-td": IPS[METVM4],
    "-wepp": IPS[METVM4],
}


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        print("Usage: python set_iemdb_etc_hosts.py <local|proxy>")
        return
    data = open("/etc/hosts").read()
    result = []
    for line in data.split("\n"):
        result.append(line)
        if line.startswith("# ---AUTOGEN---"):
            print("Found ---AUTOGEN---")
            break
    for dbname in LOOKUP:
        ip = LOOKUP[dbname] if argv[1] == "proxy" else "127.0.0.1"
        result.append("%s iemdb%s.local" % (ip, dbname))
    print("added %s entries" % (len(LOOKUP),))
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, ("\n".join(result)).encode("ascii"))
    os.write(tmpfd, b"\n")
    os.close(tmpfd)
    os.rename(tmpfn, "/etc/hosts")
    os.chmod("/etc/hosts", 0o644)


if __name__ == "__main__":
    main(sys.argv)
