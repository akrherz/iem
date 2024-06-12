"""Look into which autoplots have not been used in a while"""

import re

import pandas as pd
from pyiem.database import get_dbconnc

QRE = re.compile("q=([0-9]+)")
NO_FEATURES = [
    17,  # is referenced by canonical page
    31,  # not useful
    33,  # too pidgeon-holed
    68,  # nws unique VTEC types per year
    81,  # stddev daily temps, too boring
    91,  # hated by myself and the general public
    96,  # one-off showing precip biases
    94,  # one-off showing temp biases
    111,
    112,
    114,
    117,
    118,
    119,
    120,
    121,
    122,
    123,
    124,  # climodat text-only reports
    141,  # yieldfx plots
    144,  # soil temp periods, too fragile of data to be useful
    152,  # growing season differences, too noisey
    158,  # Tall towers plot
    177,  # ISUSM plot linked to other app
    203,  # Handled by dedicated PHP page
]


def main():
    """DO Something"""
    pgconn, cursor = get_dbconnc("mesosite")

    cursor.execute(
        "SELECT valid, appurl from feature WHERE appurl is not null "
        "and appurl != ''"
    )
    rows = {}
    for row in cursor:
        appurl = row["appurl"]
        valid = row["valid"]
        if appurl.find("/plotting/auto/") != 0:
            continue
        tokens = QRE.findall(appurl)
        if not tokens:
            print(f"appurl: {appurl} valid: {valid} failed RE")
            continue
        appid = int(tokens[0])
        if appid in NO_FEATURES:
            continue
        res = rows.setdefault(appid, valid)
        if res < valid:
            rows[appid] = valid
    pgconn.close()
    if not rows:
        print("No data found")
        return
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.columns = ["valid"]
    maxval = df.index.max()
    for i in range(1, maxval):
        if i not in rows and i not in NO_FEATURES:
            print(f"No entries for: {i:4.0f}")
    df = df.sort_values(by="valid")
    print(df.head(20))


if __name__ == "__main__":
    main()
