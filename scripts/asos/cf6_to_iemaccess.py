"""Merge the CF6 Processed Data.

Run from RUN_12Z.sh, RUN_0Z.sh for past 48 hours of data
"""
import sys
from datetime import date

import pandas as pd
from metpy.units import units
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


def comp(old, new):
    """Figure out if this value is new or not."""
    if pd.isnull(new) and pd.isnull(old):
        return False
    # If the new value is null, we want this as the value should be null
    if pd.isnull(new):
        return True
    if old == new:
        return False
    if abs(new - old) < 0.01:
        return False
    return True


def get_data(argv):
    """Figure out what data we want."""
    params = {}
    lmt = "updated > (now() - '48 hours'::interval)"
    if len(argv) == 4:
        lmt = "valid = :valid"
        params["valid"] = date(int(argv[1]), int(argv[2]), int(argv[3]))

    with get_sqlalchemy_conn("iem") as conn:
        cf6 = pd.read_sql(
            text(f"SELECT * from cf6_data where {lmt} ORDER by station ASC"),
            conn,
            params=params,
        )
    for col in ["avg_smph", "max_smph", "gust_smph"]:
        cf6[col.replace("smph", "sknt")] = (
            (units("miles/hour") * cf6[col].values).to(units("knots")).m
        )
    LOG.info("Found %s CF6 entries for syncing", len(cf6.index))
    return cf6


def update_climodat(cf6df, xref, valid):
    """Update iemaccess."""
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            "select station, high, low, precip from alldata WHERE day = %s",
            conn,
            params=(valid,),
            index_col="station",
        )
    df = cf6df.join(xref, how="inner")
    if df.empty:
        return
    dbconn = get_dbconn("coop")
    cursor = dbconn.cursor()
    uvals = 0
    urows = 0
    for _station, row in df.iterrows():
        for clsid in [row["climodat_src"], row["climodat_dest"]]:
            if clsid not in obs.index:
                LOG.warning("No climodat data for %s[%s]?", clsid, valid)
                continue
            current = obs.loc[clsid]
            work = []
            params = []
            for col in ["high", "low", "precip"]:
                if not comp(current[col], row[col]):
                    continue
                uvals += 1
                work.append(f"{col} = %s")
                if pd.isna(row[col]):
                    params.append(None)
                else:
                    params.append(
                        row[col] if col == "precip" else int(row[col])
                    )
                LOG.info("%s %s %s->%s", clsid, col, current[col], row[col])
            if not work:
                continue
            params.append(clsid)
            params.append(valid)
            urows += 1
            cursor.execute(
                f"UPDATE alldata SET {','.join(work)} WHERE station = %s and "
                "day = %s",
                params,
            )

    cursor.close()
    dbconn.commit()
    LOG.info("%s updated %s values over %s rows", valid, uvals, urows)


def update_iemaccess(cf6df, valid):
    """Update iemaccess."""
    dbconn = get_dbconn("iem")
    table = f"summary_{valid.year}"
    with get_sqlalchemy_conn("iem") as conn:
        # NB: we should not have any of these station IDs in the COOP network
        obs = pd.read_sql(
            f"""
            SELECT s.*, t.network,
            case when length(t.id) = 3 then 'K'||t.id else t.id end
            as station from {table} s JOIN
            stations t on (s.iemid = t.iemid) WHERE s.day = %s and
            (t.network ~* 'ASOS' or (t.network ~* 'DCP' and length(id) < 5))
            ORDER by station ASC
            """,
            conn,
            params=(valid,),
            index_col=None,
        )

    df = cf6df.merge(
        obs, left_index=True, right_on="station", suffixes=("_cf6", "_ob")
    )
    obscols = (
        "max_tmpf min_tmpf pday snow_ob snowd avg_sknt_ob max_sknt_ob "
        "avg_drct max_gust max_drct"
    ).split()
    cf6cols = (
        "high low precip snow_cf6 snowd_12z avg_sknt_cf6 max_sknt_cf6 "
        "avg_drct gust_sknt gust_drct"
    ).split()
    cursor = dbconn.cursor()
    uvals = 0
    urows = 0
    for _id, row in df.iterrows():
        if pd.isnull(row["iemid"]):
            # Lots of false positives here, like WFOs
            LOG.info("Yikes, station %s has no iemid?", row["station"])
            continue
        work = []
        params = []
        for ocol, ccol in zip(obscols, cf6cols):
            if not comp(row[ocol], row[ccol]):
                continue
            uvals += 1
            work.append(f"{ocol.replace('_ob', '')} = %s")
            params.append(None if pd.isna(row[ccol]) else row[ccol])
        if not work:
            continue
        params.append(int(row["iemid"]))
        params.append(valid)
        urows += 1
        cursor.execute(
            f"UPDATE {table} SET {','.join(work)} WHERE iemid = %s and "
            "day = %s",
            params,
        )

    cursor.close()
    dbconn.commit()
    LOG.info("%s updated %s values over %s rows", valid, uvals, urows)


def build_xref():
    """Build a cross reference"""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            """
            with data as (
                select r.iemid, t.id as climodat_src,
                t.iemid as climodat_src_iemid from station_threading r JOIN
                stations t on (r.source_iemid = t.iemid)
                WHERE end_date is null),
            agg as (
                select t.id as climodat_dest, climodat_src, climodat_src_iemid
                from data d JOIN stations t on (d.iemid = t.iemid)),
            agg2 as (
                select climodat_src, climodat_dest,
                split_part(value, '|', 1) as icao from
                agg a JOIN station_attributes s on
                (a.climodat_src_iemid = s.iemid) WHERE value ~* 'ASOS')
            select climodat_src, climodat_dest,
            case when length(icao) = 3 then 'K'||icao else icao end as station
            from agg2
            """,
            conn,
            index_col="station",
        )
    return df


def main(argv):
    """Go Main Go."""
    cf6 = get_data(argv)
    xref = build_xref()

    for valid, gdf in cf6.groupby("valid"):
        update_climodat(gdf.copy().set_index("station"), xref, valid)
        update_iemaccess(gdf.copy().set_index("station"), valid)


if __name__ == "__main__":
    main(sys.argv)
