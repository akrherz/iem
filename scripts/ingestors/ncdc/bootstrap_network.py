"""Look for stations to expand climodat"""
import sys

import pandas as pd


def read_inventory():
    """Read the inventory table"""
    rows = []
    for line in open("ghcnd-inventory.txt"):
        if not line.startswith("USC"):
            continue
        rows.append([line[:11], line[31:35], line[36:40], line[41:45]])
    df = pd.DataFrame(rows, columns=["sid", "vname", "start", "end"])
    df["years"] = (
        pd.to_numeric(df["end"], errors="coerce")
        - pd.to_numeric(df["start"], errors="coerce")
        + 1
    )
    return df


def read_stations(state):
    """Read the station table"""
    rows = []
    for line in open("ghcnd-stations.txt"):
        if not line.startswith("USC") or line[38:40] != state:
            continue
        rows.append(
            [
                line[:11],
                line[13:20],
                line[21:30],
                line[31:37],
                line[38:40],
                line[41:76].strip(),
            ]
        )
    df = pd.DataFrame(
        rows, columns=["sid", "lat", "lon", "elev", "state", "name"]
    )
    df = df.set_index("sid")
    return df


def main(argv):
    """Go!"""
    output = open("insert.sql", "w")
    state = argv[1]
    df = read_stations(state)
    inv = read_inventory()
    for sid, row in df.iterrows():
        invdf = inv[inv["sid"] == sid]
        years = invdf.groupby("vname").sum()
        maxyear = invdf.groupby("vname").max()
        # We'd like stations with at least TMAX, TMIN and PRCP
        useme = True
        for vname in ["TMAX", "TMIN", "PRCP"]:
            if vname not in years.index:
                useme = False
                continue
            if (
                years.at[vname, "years"] < 50
                or maxyear.at[vname, "end"] < "2010"
            ):
                useme = False
                continue

        if not useme:
            continue
        print("Candidate %s" % (sid,))
        output.write(
            """
        INSERT into stations(id, name, network, country, state,
        plot_name, elevation, online, metasite, geom) VALUES
        ('%s%s', '%s', '%sCLIMATE',
         'US', '%s', '%s', %s, 't', 't', 'SRID=4326;POINT(%s %s)');
        """
            % (
                state,
                sid[-4:],
                row["name"],
                state,
                state,
                row["name"],
                row["elev"],
                row["lon"],
                row["lat"],
            )
        )
    output.close()


if __name__ == "__main__":
    main(sys.argv)
