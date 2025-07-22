"""Create the RR5 SHEF product that the Weather Bureau Desires

Run from RUN_10MIN.sh
"""

import os
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.tracker import loadqc
from pyiem.util import c2f, utc


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
            sql_helper("""
            with recent as (
                select *,
                rank() OVER (PARTITION by station ORDER by valid desc)
                from sm_minute where valid > now() - '90 minutes'::interval
            )
            select * from recent where rank = 1
            """),
            dbconn,
            index_col="station",
        )
    df["valid"] = df["valid"].dt.tz_convert(ZoneInfo("America/Chicago"))
    df["tmpf"] = c2f(df["tair_c_avg_qc"].values)
    for station, row in df.iterrows():
        q = qcdict.get(station, {})
        if "tmpf" in q or pd.isna(row["tmpf"]):
            tmpf = "M"
        else:
            tmpf = f"{row['tmpf']:.1f}"
        # prevent duplicated entries due to having both sensors
        mv_done = []
        tv_done = []
        tokens = []
        for depth in [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]:
            for prefix in ["", "sv_"]:
                varname = f"{prefix}vwc{depth}_qc"
                if varname in df.columns and depth not in mv_done:
                    value = row[varname]
                    if pd.notna(value):
                        tokens.append(
                            mt("MVIRZZ", value * 100.0, str(depth), q)
                        )
                        mv_done.append(depth)
                varname = f"{prefix}t{depth}_c_avg_qc"
                if varname in df.columns and depth not in tv_done:
                    value = row[varname]
                    if pd.notna(value):
                        tokens.append(mt("TVIRZZ", c2f(value), str(depth), q))
                        tv_done.append(depth)
                varname = f"{prefix}t{depth}_qc"
                if varname in df.columns and depth not in tv_done:
                    value = row[varname]
                    if pd.notna(value):
                        tokens.append(mt("TVIRZZ", c2f(value), str(depth), q))
                        tv_done.append(depth)
        full_message = (
            f".A {station} {row['valid']:%Y%m%d} C DH{row['valid']:%H%M}"
            f"/TAIRZZ {tmpf} {' '.join(tokens)}\n"
        )
        # We want to split the line into appropriate chunks, whilst ensuring
        # SHEF compliance
        i = 0
        parts = full_message.strip().split("/")
        line = ""
        for part in parts:
            line += f"{part} /"
            if len(line) > 80:
                if i > 0:
                    line = f".A{i} /{line}"
                data += line.rstrip("/").strip() + "\n"
                line = ""
                i += 1
        if line:
            if i > 0:
                line = f".A{i} /{line}"
            data += line.rstrip("/").strip() + "\n"
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
