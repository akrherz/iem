"""Compare what we have for stations and what NCEI has for GHCN"""
import sys

import pandas as pd
from pyiem.network import Table as NetworkTable


def read_table(state):
    """Load up what NCEI has"""
    rows = []
    for line in open("ghcnd-stations.txt"):
        if not line.startswith("US") or line[38:40] != state:
            continue
        fullid = line[:11]
        name = line[41:71].strip()
        rows.append(dict(name=name, fullid=fullid, lastfour=fullid[-4:]))
    return pd.DataFrame(rows)


def main(argv):
    """Can we do it?"""
    nt = NetworkTable("%sCLIMATE" % (argv[1],))
    ncei = read_table(argv[1])
    for sid in nt.sts:
        if sid[2] == "C" or sid[-4:] == "0000":
            continue
        df = ncei[ncei["fullid"] == nt.sts[sid]["ncdc81"]]
        if len(df.index) == 1:
            continue
        print(
            ("Resolve Conflict: iem: %s %s ncdc81: %s ncei: %s")
            % (sid, nt.sts[sid]["name"], nt.sts[sid]["ncdc81"], df)
        )


if __name__ == "__main__":
    main(sys.argv)
