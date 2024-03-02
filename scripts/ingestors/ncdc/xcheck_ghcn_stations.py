"""Compare what we have for stations and what NCEI has for GHCN"""

import sys

import pandas as pd
from pyiem.network import Table as NetworkTable


def read_table(state):
    """Load up what NCEI has"""
    rows = []
    with open("ghcnd-stations.txt", encoding="ascii") as fh:
        for line in fh:
            if not line.startswith("US") or line[38:40] != state:
                continue
            fullid = line[:11]
            name = line[41:71].strip()
            rows.append(
                {"name": name, "fullid": fullid, "lastfour": fullid[-4:]}
            )
    return pd.DataFrame(rows)


def main(argv):
    """Can we do it?"""
    nt = NetworkTable(f"{argv[1]}CLIMATE")
    ncei = read_table(argv[1])
    for sid in nt.sts:
        if sid[2] == "C" or sid[-4:] == "0000":
            continue
        df = ncei[ncei["fullid"] == nt.sts[sid]["ncdc81"]]
        if len(df.index) == 1:
            continue
        print(
            f"Resolve Conflict: iem: {sid} {nt.sts[sid]['name']} "
            f"ncdc81: {nt.sts[sid]['ncei81']} ncei: {df}"
        )


if __name__ == "__main__":
    main(sys.argv)
