"""Parse monthly IDOT Maint Report.

1. Only sites in `CALSITES` get calibrated as others will just have their
entire sensors replaced when outside of bounds.
2. There is no flag that denotes if a calibration even happened :/
"""

import re
from datetime import datetime

import click
import pandas as pd
from pyiem.database import get_dbconn

# These sites have old sensors that still can be calibrated
CALSITES = "TVK CKP FXY GGI IIB IFA MPZ I75 OOA PEA PRO VTI".split()
CALINFO = re.compile(
    (
        r".*AWOS.*\s+([0-9\-\.]+)\s*/\s*([0-9\-\.]+)\s+"
        r".*AWOS.*\s+([0-9\-\.]+)\s*/\s*([0-9\-\.]+)"
    ),
    re.IGNORECASE,
)
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"


@click.command()
@click.option("--filename", help="CSV file to parse", required=True)
@click.option("--commit", is_flag=True, help="Actually commit to database")
def main(filename: str, commit: bool) -> None:
    """Go Main"""
    # Use SSH proxy
    pgconn = get_dbconn("portfolio", user="mesonet")
    pcursor = pgconn.cursor()

    df = pd.read_csv(filename, encoding="cp1252")
    done = []
    for _, row in df.iterrows():
        faa = row["FAA Code"]
        comment = ""
        if faa not in CALSITES:
            comment = " [FYI Check Made]"
        key = faa + row["Visit Date"]
        if key in done:
            continue
        done.append(key)
        date = datetime.strptime(row["Visit Date"], "%m-%d-%Y")
        descr = (
            row["Description"]
            .lower()
            .replace("\r", "")
            .replace("\n", " ")
            .replace("std", "/")
            .replace("/standard", "/")
            .replace("standard", "/")
            .replace("/ temp ", "/ ")
            .replace("/ dew ", "/ ")
        )
        if descr.startswith("site offline"):
            continue
        parts = re.findall(CALINFO, descr)
        if not parts:
            print(FAIL + descr + ENDC)
            continue
        sql = """
        INSERT into iem_calibration(station, portfolio, valid, parameter,
        adjustment, final, comments) values (%s, 'iaawos', %s, %s, %s, %s, %s)
        """
        comment = (
            row["Description"]
            .replace('"', "")
            .replace("\r", "")
            .replace("\n", " ")
            + comment
        )
        tempadj = float(parts[0][1]) - float(parts[0][0])
        p2 = parts[0][2]
        if p2.endswith("."):
            p2 = p2[:-1]
        args = (
            faa,
            date.strftime("%Y-%m-%d"),
            "tmpf",
            tempadj,
            p2,
            comment,
        )
        if commit:
            pcursor.execute(
                """
                delete from iem_calibration where station = %s and valid = %s
                and parameter = %s
                """,
                (faa, date.strftime("%Y-%m-%d"), "tmpf"),
            )
            pcursor.execute(sql, args)

        dewpadj = float(parts[0][3]) - float(p2)
        args = (
            faa,
            date.strftime("%Y-%m-%d"),
            "dwpf",
            dewpadj,
            parts[0][3],
            comment,
        )
        if commit:
            pcursor.execute(
                """
                delete from iem_calibration where station = %s and valid = %s
                and parameter = %s
                """,
                (faa, date.strftime("%Y-%m-%d"), "dwpf"),
            )
            pcursor.execute(sql, args)

        print(
            f"--> {faa} [{date}] TMPF: {parts[0][1]} ({tempadj}) "
            f"DWPF: {parts[0][3]} ({dewpadj}){comment}"
        )

    if not commit:
        print("WARNING: Disabled, call with --commit to enable")
    else:
        pcursor.close()
        pgconn.commit()
        pgconn.close()


if __name__ == "__main__":
    main()
