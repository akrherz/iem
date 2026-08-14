"""Use data provided by ACIS to replace climodat data.

# Implementation Notes

- If either high or low temperature is missing in ACIS, we will not update
  the database other than to ensure temp_estimated is set to True.
"""

import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
import pandas as pd
import requests
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE, ncei_state_codes
from pyiem.util import logger, utc

LOG = logger()
SERVICE = "https://data.rcc-acis.org/StnData"
METASERVICE = "https://data.rcc-acis.org/StnMeta"


def compute_por(acis_station) -> tuple[date, date]:
    """Need to ask ACIS what the POR is based on variables, not SIDs.

    Result payload looks like:
     {"meta":[{"valid_daterange":[["1904-02-06","2024-04-25"],...]}]}
    """
    payload = {
        "sids": acis_station,
        "meta": "valid_daterange",
        "elems": "maxt,mint,pcpn",
    }
    meta = requests.post(
        f"{METASERVICE}?sid={acis_station}", json=payload, timeout=60
    ).json()
    dates = []
    for pair in meta["meta"][0]["valid_daterange"]:
        for stamp in pair:
            if stamp.startswith(("0001", "9999")):
                continue
            dates.append(datetime.strptime(stamp, "%Y-%m-%d").date())
    return min(dates), max(dates)


def build_acis_dataframe(acis_station: str, meta: dict) -> pd.DataFrame:
    """Download and compute the acis dataframe."""
    fmt = "%Y-%m-%d"
    try:
        meta_mindt, meta_maxdt = compute_por(acis_station)
    except Exception as exp:
        LOG.exception(exp)
        return pd.DataFrame()
    # If this station is offline, we don't want to ask for data past the
    # archive_end date.  The station could be a precip-only site...
    edate = meta["attributes"].get("CEILING")
    if edate is None:
        if meta["online"]:
            edate = f"{meta_maxdt:%Y-%m-%d}"
        else:
            edate = meta["archive_end"].strftime(fmt)
    payload = {
        "sid": acis_station,
        "meta": "tzo",
        "sdate": meta["attributes"].get("FLOOR", f"{meta_mindt:%Y-%m-%d}"),
        "edate": meta["attributes"].get("CEIL", edate),
        "elems": [
            {"name": "maxt", "add": "t"},
            {"name": "mint"},
            {"name": "pcpn", "add": "t"},
            {"name": "snow"},
            {"name": "snwd"},
        ],
    }
    j = {}
    for attempt in range(3):
        try:
            resp = requests.post(SERVICE, json=payload, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            break
        except Exception:
            LOG.warning(
                "Failed to query ACIS for %s, sleeping 60 seconds",
                acis_station,
            )
            # Give server some time to recover from transient errors
            time.sleep(60)
        if attempt == 2:
            LOG.error(
                "Failed to query ACIS for %s after 3 attempts, giving up",
                acis_station,
            )
            return pd.DataFrame()
    if "data" not in j:
        LOG.info("No Data!, content=%s", resp.content)
        return pd.DataFrame()

    acis = pd.DataFrame(
        j["data"],
        columns="day ahigh alow aprecip asnow asnowd".split(),
    )
    acis["day"] = pd.to_datetime(acis["day"])
    # Figure out the offset so that we can compute the proper timestamp
    timezone_offset_hours = j["meta"]["tzo"] * -1
    tzinfo = ZoneInfo(meta["tzname"])

    def _compute_hour(row: np.ndarray) -> int:
        """Rectify this standard time hour back to DST aware."""
        day, hour = row
        # This is a special case.
        if hour == 24:
            return 24
        dt = utc(day.year, day.month, day.day, int(hour)) + timedelta(
            hours=timezone_offset_hours
        )
        dsthr = dt.astimezone(tzinfo).hour
        return dsthr

    for col in "ahigh aprecip".split():
        acis[[col, f"{col}_hour"]] = pd.DataFrame(
            acis[col].tolist(),
            index=acis.index,
        )
        # hour values of -1 are missing
        acis.loc[acis[f"{col}_hour"] < 0, f"{col}_hour"] = np.nan
        # This is ugly, we need to convert the value back to the DST aware
        # value used by the IEM
        goodrows = acis[f"{col}_hour"].notna()
        acis.loc[goodrows, f"{col}_hour"] = acis.loc[
            goodrows, ["day", f"{col}_hour"]
        ].apply(_compute_hour, raw=True, axis=1)

    return acis


def do(meta: dict, station: str, acis_station: str) -> int:
    """Do the query and work."""
    table = f"alldata_{station[:2]}"
    acis = build_acis_dataframe(acis_station, meta)
    if acis.empty:
        LOG.warning("ACIS returned no data for %s", acis_station)
        return 0
    # If either ahigh or alow is missing, set both to missing
    acis.loc[
        (acis["ahigh"] == "M") | (acis["alow"] == "M"),
        ["ahigh", "alow", "ahigh_hour"],
    ] = np.nan
    # if either aprecip or asnow has a `A` character, set to missing
    acis.loc[acis["aprecip"].str.contains("A"), "aprecip"] = np.nan
    acis.loc[acis["asnow"].str.contains("A"), "asnow"] = np.nan
    # Rectify the name to match IEM database
    acis = acis.rename(columns={"ahigh_hour": "atemp_hour"}).replace(
        {"T": TRACE_VALUE, "M": np.nan, "S": np.nan}
    )
    # fill out estimated flags
    acis["atemp_estimated"] = acis["ahigh"].isna()
    acis["aprecip_estimated"] = acis["aprecip"].isna()

    LOG.info("Loaded %s rows from ACIS", len(acis.index))
    acis = acis.set_index("day")
    pgconn = get_dbconn("coop")
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            sql_helper("""
            SELECT day, high, low, precip, snow, snowd, temp_hour, precip_hour,
            temp_estimated, precip_estimated, true as dbhas
            from alldata WHERE station = :station ORDER by day ASC
            """),
            conn,
            params={"station": station},
            index_col="day",
        )
    LOG.info("Loaded %s rows from IEM", len(obs.index))
    cursor = pgconn.cursor()
    # join the tables
    df = acis.join(obs, how="left")
    df["temp_estimated"] = df["temp_estimated"].fillna(True)
    df["precip_estimated"] = df["precip_estimated"].fillna(True)
    df["dbhas"] = df["dbhas"].fillna(False)
    # If the database does not have this, we need to update it
    df["dirty"] = ~df["dbhas"]
    for col in ["high", "low", "temp_hour", "precip_hour"]:
        for prefix in ["a", ""]:
            df[f"{prefix}{col}"] = df[f"{prefix}{col}"].astype(
                "Int64", errors="raise"
            )
    for col in ["precip", "snow", "snowd"]:
        for prefix in ["a", ""]:
            df[f"{prefix}{col}"] = (
                df[f"{prefix}{col}"]
                .fillna(np.nan)
                .astype("float64", errors="raise")
            )
    for col in ["temp_estimated", "precip_estimated"]:
        for prefix in ["a", ""]:
            df[f"{prefix}{col}"] = (
                df[f"{prefix}{col}"]
                .fillna(True)
                .astype("bool", errors="raise")
            )
    for col in ["dbhas", "dirty"]:
        df[col] = df[col].astype("bool", errors="raise")

    updates = {}
    cols = "high low precip snow snowd temp_hour precip_hour".split()
    for col in cols:
        updates[col] = 0
    # Ensure we have no columns of object dtype
    if df.select_dtypes(include="object").columns.any():
        LOG.info(df.select_dtypes(include="object").columns)
        LOG.info(df.dtypes)
        raise ValueError("We have object dtype columns")
    df["station"] = station
    # account for the case where we have a high or low, but not both
    idx = df["ahigh"].isna() | df["alow"].isna()
    if idx.any():
        df.loc[idx, "ahigh"] = np.nan
        df.loc[idx, "alow"] = np.nan
    # find rows whereby we should be using ACIS
    for col in ["high", "low", "precip"]:
        ecol = "precip" if col == "precip" else "temp"
        idx = (
            (df[f"a{col}"].notna() & (df[f"a{col}"] != df[col]))
            | (df[f"a{col}"].isna() & ~df[f"{ecol}_estimated"])
            | (df[f"{ecol}_estimated"] & df[f"a{col}"].notna())
        )
        if idx.any():
            df.loc[idx, col] = df.loc[idx, f"a{col}"]
            df.loc[idx, f"{ecol}_hour"] = df.loc[idx, f"a{ecol}_hour"]
            df.loc[idx, f"{ecol}_estimated"] = df.loc[
                idx, f"a{ecol}_estimated"
            ]
            df.loc[idx, "dirty"] = True
            updates[col] = idx.sum()

    # for snow and snowd, it is simplier
    for col in ["snow", "snowd", "temp_hour", "precip_hour"]:
        idx = df[f"a{col}"].notna() & (df[f"a{col}"] != df[col])
        if idx.any():
            df.loc[idx, col] = df.loc[idx, f"a{col}"]
            df.loc[idx, "dirty"] = True
            updates[col] = idx.sum()

    cursor.executemany(
        f"insert into {table} (station, day, sday, year, month) "
        "values (%(station)s, %(day)s, "
        "to_char(%(day)s::date, 'mmdd'), "
        "extract(year from %(day)s::date), "
        "extract(month from %(day)s::date)) ",
        df[~df["dbhas"]].reset_index().to_dict("records"),
    )
    inserts = cursor.rowcount
    cursor.executemany(
        f"update {table} SET high = %(high)s, low = %(low)s, "
        "precip = %(precip)s, snow = %(snow)s, temp_hour = %(temp_hour)s, "
        "precip_hour = %(precip_hour)s, snowd = %(snowd)s, "
        "temp_estimated = %(temp_estimated)s, "
        "precip_estimated = %(precip_estimated)s "
        "WHERE station = %(station)s and day = %(day)s",
        df[df["dirty"]].reset_index().to_dict("records"),
    )
    if df["dirty"].any() or inserts > 0:
        LOG.warning(
            "%s New:%s Updates H:%s HH:%s L:%s P:%s PH:%s S:%s D:%s",
            station,
            inserts,
            updates["high"],
            updates["temp_hour"],
            updates["low"],
            updates["precip"],
            updates["precip_hour"],
            updates["snow"],
            updates["snowd"],
        )
    cursor.close()
    pgconn.commit()
    return max(updates.values())


@click.command()
@click.option("--state", help="Two character state identifier")
@click.option("--station", help="IEM Station Identifier")
@click.option("--acis_station", help="ACIS Station Identifier")
def main(state: str | None, station: str | None, acis_station: str | None):
    """Do what is asked."""
    # Only run cron job for online sites
    nt = NetworkTable(
        f"{state if state is not None else station[:2]}CLIMATE",
        only_online=False,
    )

    def _worker(sid, acis_station):
        """Do work."""
        do(nt.sts[sid], sid, acis_station)

    if state is not None:
        for sid in nt.sts:
            if sid[2] == "C" or sid[2:] == "0000":
                continue
            astation = ncei_state_codes[state] + sid[2:]
            if sid[2] in ["K", "P"]:
                astation = sid[2:]
            if sid[2] == "T":
                astation = f"{sid[3:]}thr"
            LOG.info("Guessing ACIS station as: %s", astation)
            _worker(sid, astation)
    elif station is not None and acis_station is None:
        astation = ncei_state_codes[station[:2]] + station[2:]
        if station[2] in ["K", "P"]:
            astation = station[2:]
        if station[2] == "T":
            astation = f"{station[3:]}thr"
        LOG.info("Guessing ACIS station as: %s", astation)
        _worker(station, astation)
    else:
        _worker(station, acis_station)


if __name__ == "__main__":
    main()
