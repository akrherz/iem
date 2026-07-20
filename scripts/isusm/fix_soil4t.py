"""Quality control our 4 inch soil temperature data.

Called from soilm_ingest.py
Called after ERA5Land ingest completes
"""

from datetime import date, datetime, timezone

import click
import pandas as pd
import requests
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger
from sqlalchemy.engine import Connection

LOG = logger()
# The amount we allow the abs bias of the analysis vs obs to be.  This is
# rather forgiving, allows 25% and 50% percentile values +/- this value
BULK_QC_THRESHOLD = 5.0
# The amount we allow the abs bias of the analysis vs obs to be.
MEAN_QC_THRESHOLD = 2.0


def setval(
    conn: Connection,
    qcdf: pd.DataFrame,
    station: str,
    col: str,
    ob: float | None,
    dt: date,
    newval: float,
    flag: str,
):
    """We have something to set."""
    (LOG.warning if flag == "E" else LOG.info)(
        "%s %s %s %s -> %.1f (%s) [%s]",
        station,
        dt,
        col,
        None if pd.isna(ob) else f"{ob:.1f}",
        newval,
        None if pd.isna(ob) else f"{(ob - newval):.1f}",
        flag,
    )
    # Update dataframe to reflect how we updated the database...
    if flag != "P":
        qcdf.at[station, "update_hourly"] = True
    qcdf.at[station, f"ob_{col}_f"] = flag
    qcdf.at[station, f"ob_{col}_qc"] = newval
    conn.execute(
        sql_helper(
            """
        UPDATE sm_daily SET {col}_qc = :newval, {col}_f = :flag WHERE
        station = :station and valid = :valid
        """,
            col=col,
        ),
        {
            "station": station,
            "valid": dt,
            "newval": newval,
            "flag": flag,
        },
    )


def do_checks(
    qcdf: pd.DataFrame, conn: Connection, dt: date, col: str, force_qc: bool
):
    # We'll take any value
    obcol = f"ob_{col}"
    for station, row in qcdf.iterrows():
        # If Ob is None, we have no choice
        if pd.isna(row[obcol]) or row["force_qc"]:
            setval(conn, qcdf, station, col, row[obcol], dt, row[col], "E")
            continue
        # Passes if value within 2 C of IEMRE
        if abs(row[obcol] - row[col]) <= 2:
            LOG.info(
                "%s passes2c %s ob:%.2f iemre:%.2f",
                station,
                obcol,
                row[obcol],
                row[col],
            )
            # Set the QC value to observed value
            setval(conn, qcdf, station, col, row[obcol], dt, row[obcol], "P")
            continue
        # Passes if within bounds of Iowa values
        if qcdf[col].min() <= row[obcol] <= qcdf[col].max():
            LOG.info(
                "%s passesbnd %s ob:%.2f iemre:%.2f",
                station,
                col,
                row[obcol],
                row[col],
            )
            # Set the QC value to observed value
            setval(conn, qcdf, station, col, row[obcol], dt, row[obcol], "P")
            continue
        # Passes if bulk qc failed and we aren't forcing it for this row
        if not force_qc and not row["force_qc"]:
            LOG.info(
                "%s not_forced %s ob:%.2f iemre:%.2f",
                station,
                col,
                row[obcol],
                row[col],
            )
            continue
        # We fail
        setval(conn, qcdf, station, col, row[obcol], dt, row[col], "E")


def passes_bulk_check(qcdf: pd.DataFrame) -> bool:
    """Can we rely on the model analysis?"""
    # Here lies dragons.  We want to check for the situation when the model
    # based analysis is wildly off and we don't want that polluting the
    # observations. How can we reliably tell when that's the case?
    # First, lets build up some bulk statistics comparing the two datasets
    compstats = (qcdf["ob_t4_c_avg"] - qcdf["t4_c_avg"]).describe()
    # Lets call it good if the 25% and 75% percentil values are within
    # -/+ BULK_QC_THRESHOLD
    passes = (
        compstats["25%"] >= -BULK_QC_THRESHOLD
        and compstats["75%"] <= BULK_QC_THRESHOLD
    ) or (abs(compstats["mean"]) < MEAN_QC_THRESHOLD)
    loglvl = LOG.info if passes else LOG.warning
    loglvl(
        "Bulk QC %s with P25:%.1f P75:%.1f +/-:%.1f, Mean:%.1f +/-%.1f\n%s",
        "passed" if passes else "failed",
        compstats["25%"],
        compstats["75%"],
        BULK_QC_THRESHOLD,
        compstats["mean"],
        MEAN_QC_THRESHOLD,
        compstats.to_markdown(),
    )
    return passes


@with_sqlalchemy_conn("isuag")
def update_hourly(
    station: str, dt: date, nt: NetworkTable, conn: Connection | None = None
):
    """If we have estimated daily data, we need to update hourly verbatim.."""
    # Go fetch me the IEMRE value!
    uri = (
        f"https://mesonet.agron.iastate.edu/iemre/hourly.py?"
        f"date={dt:%Y-%m-%d}&"
        f"lat={nt.sts[station]['lat']:.2f}&"
        f"lon={nt.sts[station]['lon']:.2f}&format=json"
    )
    j = requests.get(uri, timeout=60).json()
    for entry in j["data"]:
        dt = datetime.strptime(entry["valid_utc"], "%Y-%m-%dT%H:%MZ").replace(
            tzinfo=timezone.utc
        )
        t4_c = convert_value(entry["soil4t_f"], "degF", "degC")
        if pd.isna(t4_c):
            LOG.warning("%s %s IEMRE is missing", station, dt)
            continue
        conn.execute(
            sql_helper("""
            UPDATE sm_hourly SET t4_c_avg_qc = :t4_c, t4_c_avg_f = 'E' WHERE
            station = :station and valid = :valid
            """),
            {"t4_c": t4_c, "station": station, "valid": dt},
        )
    conn.commit()


@with_sqlalchemy_conn("isuag")
def check_date(
    dt: date, nt: NetworkTable, conn: Connection | None = None
) -> pd.DataFrame:
    """Look this date over and compare with IEMRE."""
    res = conn.execute(
        sql_helper("""
    SELECT station,
    t4_c_min, t4_c_min_f, t4_c_min_qc,
    t4_c_avg, t4_c_avg_f, t4_c_avg_qc,
    t4_c_max, t4_c_max_f, t4_c_max_qc,
    'f'::bool as force_qc,
    'f'::bool as update_hourly
    from sm_daily where valid = :valid ORDER by station ASC"""),
        {"valid": dt},
    )
    qcrows = []
    for row in res.mappings():
        station = row["station"]
        if nt.sts[station]["attributes"].get("NO_4INCH") == "1":
            LOG.info("Skipping %s as NO_4INCH", station)
            continue
        # Go fetch me the IEMRE value!
        uri = (
            f"https://mesonet.agron.iastate.edu/iemre/daily/{dt:%Y-%m-%d}/"
            f"{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        j = requests.get(uri, timeout=60).json()
        iemre = j["data"][0]
        iemre_low = convert_value(iemre["soil4t_low_f"], "degF", "degC")
        iemre_high = convert_value(iemre["soil4t_high_f"], "degF", "degC")
        if pd.isna(iemre_high) or pd.isna(iemre_low):
            LOG.warning("%s %s IEMRE is missing", station, dt)
            continue
        iemre_avg = (iemre_high + iemre_low) / 2.0
        force_qc = row["force_qc"]
        if (
            row["t4_c_min"] is not None
            and row["t4_c_max"] is not None
            and abs(row["t4_c_max"] - row["t4_c_min"]) < 0.01  # winter
        ):
            LOG.info(
                "%s has ~constant value %s -> %s",
                station,
                row["t4_c_min"],
                row["t4_c_max"],
            )
            # Exclude data from subsequent bulk QC check.
            force_qc = True

        qcrows.append(
            {
                "station": station,
                "ob_t4_c_avg": row["t4_c_avg"],
                "ob_t4_c_avg_f": row["t4_c_avg_f"],
                "ob_t4_c_avg_qc": row["t4_c_avg_qc"],
                "t4_c_avg": iemre_avg,
                "ob_t4_c_min": row["t4_c_min"],
                "ob_t4_c_min_f": row["t4_c_min_f"],
                "ob_t4_c_min_qc": row["t4_c_min_qc"],
                "t4_c_min": iemre_low,
                "ob_t4_c_max": row["t4_c_max"],
                "ob_t4_c_max_f": row["t4_c_max_f"],
                "ob_t4_c_max_qc": row["t4_c_max_qc"],
                "t4_c_max": iemre_high,
                "force_qc": force_qc,
                "update_hourly": row["update_hourly"],
            }
        )
    qcdf = pd.DataFrame(qcrows).set_index("station")
    force_qc = passes_bulk_check(qcdf[~qcdf["force_qc"]])
    for col in ["t4_c_avg", "t4_c_min", "t4_c_max"]:
        do_checks(qcdf, conn, dt, col, force_qc)
    conn.commit()
    return qcdf


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
@click.option("--dumpfilename", help="Dump computed data to csv filename")
def main(dt: datetime, dumpfilename: str | None = None):
    """Go Main Go."""
    nt = NetworkTable("ISUSM", only_online=False)
    qcdf = check_date(dt.date(), nt)
    if dumpfilename:
        LOG.info("Writing dataset to %s", dumpfilename)
        qcdf.to_csv(dumpfilename)
    for station in qcdf[qcdf["update_hourly"]].index:
        LOG.info("Updating hourly for %s with IEMRE verbatim", station)
        update_hourly(station, dt.date(), nt)


if __name__ == "__main__":
    main()
