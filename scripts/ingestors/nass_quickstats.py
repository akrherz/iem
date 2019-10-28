"""Dump NASS Quickstats to the IEM database"""
from __future__ import print_function
import sys
import subprocess
import datetime
import os

import pandas as pd
from pyiem.util import get_dbconn

TMP = "/mesonet/tmp"


def get_file():
    """Download and gunzip the file from the FTP site"""
    os.chdir("/mesonet/tmp")
    if os.path.isfile("%s/qstats.txt" % (TMP,)):
        print("    skipping download as we already have the file")
        return
    for i in range(0, -7, -1):
        now = datetime.date.today() + datetime.timedelta(days=i)
        fn = "qs.crops_%s.txt.gz" % (now.strftime("%Y%m%d"),)
        cmd = ("wget -q " "ftp://ftp.nass.usda.gov/quickstats/%s") % (fn,)
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        proc.stdout.read()
        if os.path.isfile(fn):
            break

    cmd = "cd %s; mv %s qstats.txt.gz; gunzip qstats.txt.gz" % (TMP, fn)
    # Popen is async, so we need to read from it!
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    proc.stdout.read()


def database(pgconn, df):
    """Save df to the database!"""
    cursor = pgconn.cursor()
    cursor.execute("""SET TIME ZONE 'UTC'""")
    df.columns = [x.lower() for x in df.columns]
    df = df.where((pd.notnull(df)), None)
    df["num_value"] = pd.to_numeric(df["value"], errors="coerce")
    df2 = df[df["commodity_desc"].isin(["CORN", "SOYBEANS"])]
    for _, row in df2.iterrows():
        try:
            # If we are not in addall mode, we have to be careful!
            cursor.execute(
                """
            INSERT into nass_quickstats(source_desc, sector_desc,
            group_desc,
            commodity_desc,
            class_desc,
            prodn_practice_desc,
            util_practice_desc,
            statisticcat_desc,
            unit_desc,
            agg_level_desc,
            state_alpha,
            asd_code,
            county_ansi,
            zip_5,
            watershed_code,
            country_code,
            year,
            freq_desc,
            begin_code,
            end_code,
            week_ending,
            load_time,
            value,
            cv,
            num_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    row["source_desc"],
                    row["sector_desc"],
                    row["group_desc"],
                    row["commodity_desc"],
                    row["class_desc"],
                    row["prodn_practice_desc"],
                    row["util_practice_desc"],
                    row["statisticcat_desc"],
                    row["unit_desc"],
                    row["agg_level_desc"],
                    row["state_alpha"],
                    row["asd_code"],
                    row["county_ansi"],
                    row["zip_5"],
                    row["watershed_code"],
                    row["country_code"],
                    row["year"],
                    row["freq_desc"],
                    row["begin_code"],
                    row["end_code"],
                    row["week_ending"],
                    row["load_time"],
                    row["value"],
                    row["cv_%"],
                    row["num_value"],
                ),
            )
        except Exception as exp:
            print(exp)
            for key in row.keys():
                print("%s %s %s" % (key, row[key], len(str(row[key]))))
            sys.exit()
    print(
        "    processed %6s lines from %6s candidates"
        % (len(df2.index), len(df.index))
    )
    cursor.close()
    pgconn.commit()


def process(pgconn):
    """Do some work"""
    # The file is way too big (11+ GB) to be reliably read into pandas, so
    # we need to do some chunked processing.
    cursor = pgconn.cursor()
    cursor.execute("truncate nass_quickstats")
    cursor.close()
    pgconn.commit()
    header = ""
    tmpfn = None
    accumlines = 0
    for linenum, line in enumerate(open("%s/qstats.txt" % (TMP,))):
        if linenum == 0:
            header = line
        if tmpfn is None:
            tmpfn = "/mesonet/tmp/tempor.txt"
            fh = open(tmpfn, "w")
            fh.write(header + "\n")
        if linenum > 0:
            fh.write(line + "\n")
            accumlines += 1
        if accumlines >= 600000:
            fh.close()
            df = pd.read_csv(tmpfn, sep="\t", low_memory=False)
            database(pgconn, df)
            tmpfn = None
            accumlines = 0
    if accumlines > 0:
        fh.close()
        df = pd.read_csv(tmpfn, sep="\t", low_memory=False)
        database(pgconn, df)


def cleanup():
    """Cleanup after ourselves"""
    for fn in ["%s/qstats.txt" % (TMP,), "%s/tempor.txt" % (TMP,)]:
        print("    Deleted %s" % (fn,))
        os.unlink(fn)


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    print("scripts/ingestors/nass_quickstats.py")
    get_file()
    process(pgconn)
    if len(argv) == 1:
        cleanup()
    print("done...")


if __name__ == "__main__":
    main(sys.argv)
