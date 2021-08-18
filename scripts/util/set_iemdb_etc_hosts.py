"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry

129.186.185.33 iemdb iemdb2
#127.0.0.1 iemdb iemdb2

"""
import sys
import tempfile
import os

METVM4, METVM1, METVM6, METVM7, METVM2 = range(5)
IPS = (
    "172.16.170.1 172.16.171.1 172.16.172.1 172.16.173.1 172.16.174.1".split()
)
LOOKUP = {
    "": IPS[METVM6],
    "-afos": IPS[METVM6],
    "-asos": IPS[METVM6],
    "-asos1min": IPS[METVM1],
    "-awos": IPS[METVM7],
    "-coop": IPS[METVM2],
    "-frost": IPS[METVM6],
    "-hads": IPS[METVM2],
    "-hml": IPS[METVM7],
    "-id3b": IPS[METVM6],
    "-idep": IPS[METVM6],
    "-iem": IPS[METVM6],
    "-iemre": IPS[METVM2],
    "-isuag": IPS[METVM6],
    "-kcci": IPS[METVM6],
    "-mec": IPS[METVM7],
    "-mesonet": IPS[METVM6],
    "-mesosite": IPS[METVM6],
    "-mos": IPS[METVM7],
    "-nc1018": IPS[METVM6],
    "-nldn": IPS[METVM4],
    "-nwx": IPS[METVM6],
    "-openfire": IPS[METVM6],
    "-other": IPS[METVM6],
    "-portfolio": IPS[METVM6],
    "-postgis": IPS[METVM4],
    "-radar": IPS[METVM4],
    "-rtstats": IPS[METVM6],
    "-rwis": IPS[METVM6],
    "-scada": IPS[METVM6],
    "-scan": IPS[METVM6],
    "-smos": IPS[METVM2],
    "-snet": IPS[METVM7],
    "-squaw": IPS[METVM6],
    "-sustainablecorn": IPS[METVM6],
    "-talltowers": IPS[METVM2],
    "-td": IPS[METVM6],
    "-wepp": IPS[METVM6],
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
