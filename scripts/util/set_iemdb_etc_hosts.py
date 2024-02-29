"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry."""

import os
import sys
import tempfile

DB1, DB2, DB3 = range(3)
IPS = "172.16.170.1 172.16.172.1 172.16.174.1".split()
LOOKUP = {
    "": IPS[DB1],
    "-afos": IPS[DB1],
    "-asos": IPS[DB3],
    "-asos1min": IPS[DB1],
    "-awos": IPS[DB3],
    "-coop": IPS[DB1],
    "-frost": IPS[DB1],
    "-hads": IPS[DB2],
    "-hml": IPS[DB3],
    "-id3b": IPS[DB1],
    "-idep": IPS[DB1],
    "-iem": IPS[DB3],
    "-iemre": IPS[DB2],
    "-isuag": IPS[DB1],
    "-kcci": IPS[DB1],
    "-mesonet": IPS[DB1],
    "-mesosite": IPS[DB1],
    "-mos": IPS[DB1],
    "-nc1018": IPS[DB1],
    "-nldn": IPS[DB2],
    "-nwx": IPS[DB1],
    "-openfire": IPS[DB3],
    "-other": IPS[DB1],
    "-portfolio": IPS[DB1],
    "-postgis": IPS[DB2],
    "-radar": IPS[DB2],
    "-raob": IPS[DB2],
    "-rtstats": IPS[DB1],
    "-rwis": IPS[DB1],
    "-scan": IPS[DB1],
    "-smos": IPS[DB2],
    "-snet": IPS[DB3],
    "-squaw": IPS[DB1],
    "-sustainablecorn": IPS[DB1],
    "-talltowers": IPS[DB2],
    "-td": IPS[DB1],
    "-uscrn": IPS[DB1],
    "-wepp": IPS[DB1],
}


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        print("Usage: python set_iemdb_etc_hosts.py <local|proxy>")
        return
    with open("/etc/hosts", encoding="utf-8") as fh:
        data = fh.read()
    result = []
    for line in data.split("\n"):
        result.append(line)
        if line.startswith("# ---AUTOGEN---"):
            print("Found ---AUTOGEN---")
            break
    for dbname, lkp in LOOKUP.items():
        ip = lkp if argv[1] == "proxy" else "127.0.0.1"
        result.append(f"{ip} iemdb{dbname}.local")
    print(f"added {len(LOOKUP)} entries")
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, ("\n".join(result)).encode("ascii"))
    os.write(tmpfd, b"\n")
    os.close(tmpfd)
    os.rename(tmpfn, "/etc/hosts")
    os.chmod("/etc/hosts", 0o644)


if __name__ == "__main__":
    main(sys.argv)
