"""Create the RR5 SHEF product that the Weather Bureau Desires

Run from RUN_10MIN.sh
"""

import os
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.tracker import loadqc
from pyiem.util import c2f, get_sqlalchemy_conn, utc


def mt(prefix, tmpf, depth, q):
    """Properly encode a value at depth into SHEF"""
    if tmpf is None or "soil4" in q or pd.isna(tmpf):
        return ""
    val = float(depth)
    val += abs(tmpf) / 1000.0
    if tmpf < 0:
        val = 0 - val

    return f"/{prefix} {val:.3f}"


def generate_rr5():
    """Create the RR5 Data"""
    qcdict = loadqc()
    data = (
        "\n\n\n"
        ": Iowa State University Soil Moisture Network\n"
        ": Data contact Daryl Herzmann akrherz@iastate.edu\n"
        f": File generated {utc():%Y-%m-%d %H:%M} UTC\n"
    )
    with get_sqlalchemy_conn("isuag") as dbconn:
        df = pd.read_sql(
            """
            with recent as (
                select *,
                rank() OVER (PARTITION by station ORDER by valid desc)
                from sm_minute where valid > now() - '90 minutes'::interval
            )
            select *, null as tmpf, null as soilt4, null as soilt12,
            null as soilt24, null as soilt50 from recent where rank = 1
            """,
            dbconn,
            index_col="station",
        )
    df["valid"] = df["valid"].dt.tz_convert(ZoneInfo("America/Chicago"))
    df["tmpf"] = c2f(df["tair_c_avg_qc"].values)
    df["soilt4"] = c2f(df["t4_c_avg_qc"].values)
    df["soilt12"] = c2f(df["t12_c_avg_qc"].values)
    df["soilt24"] = c2f(df["t24_c_avg_qc"].values)
    df["soilt50"] = c2f(df["t50_c_avg_qc"].values)
    for station, row in df.iterrows():
        q = qcdict.get(station, {})
        if "tmpf" in q or pd.isna(row["tmpf"]):
            tmpf = "M"
        else:
            tmpf = "%.1f" % (row["tmpf"],)
        linetwo = (
            mt("MVIRGZ", row["vwc12_qc"] * 100.0, "12", q)
            + mt("MVIRGZ", row["vwc24_qc"] * 100.0, "24", q)
            + mt("MVIRGZ", row["vwc50_qc"] * 100.0, "50", q)
        )
        data += (
            f".A {station} {row['valid']:%Y%m%d} C DH{row['valid']:%H%M}"
            f"/TAIRGZ {tmpf}%s%s%s%s\n"
        ) % (
            mt("TVIRGZ", row["soilt4"], "4", q),
            mt("TVIRGZ", row["soilt12"], "12", q),
            mt("TVIRGZ", row["soilt24"], "24", q),
            mt("TVIRGZ", row["soilt50"], "50", q),
        )
        if linetwo != "":
            data += f".A1 {linetwo}\n"
    return data


def main():
    """Go Main Go"""
    rr5data = generate_rr5()
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, rr5data.encode("utf-8"))
    os.close(tmpfd)
    subprocess.call(["pqinsert", "-p", "SUADSMRR5DMX.dat", tmpfn])
    os.unlink(tmpfn)


def test_mt():
    """Conversion of values to SHEF encoded values"""
    assert mt("TV", 4, 40, {}) == "/TV 40.004"
    assert mt("TV", -4, 40, {}) == "/TV -40.004"
    assert mt("TV", 104, 40, {}) == "/TV 40.104"


if __name__ == "__main__":
    main()
