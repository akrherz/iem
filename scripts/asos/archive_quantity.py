""" Create a simple prinout of observation quanity in the database """
from calendar import month_abbr
import sys

# Third Party
from colorama import Fore, Style
import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def colorize(val, perfect, bad):
    """pretty."""
    if pd.isna(val):
        return "-----"
    if val == perfect:
        return " FULL"
    if val < bad:
        color = Fore.RED
    else:
        color = Fore.GREEN
    if val > 1.5:
        return color + f"{val:5.0f}" + Style.RESET_ALL
    return color + f"{val:5.2f}" + Style.RESET_ALL


def main(argv):
    """Go Main Go"""
    station = argv[1]
    sumvar = "freq" if len(argv) == 2 else argv[2]

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            SELECT date(valid at time zone 'UTC') as date,
            count(*) as total_obs,
            sum(case when report_type = 3 then 1 else 0 end) as routine_obs,
            sum(case when report_type in (3, 4) then 1 else 0 end) as obs
            from alldata WHERE station = %s GROUP by date ORDER by date
            """,
            conn,
            params=(station,),
            index_col="date",
        )
    df = (
        df.reindex(pd.date_range(df.index[0], df.index[-1]))
        .assign(
            possible=24,
        )
        .fillna(0)
        .resample("m")
        .sum()
        .assign(
            year=lambda df_: df_.index.year,
            month=lambda df_: df_.index.month,
            freq=lambda df_: df_["routine_obs"] / df_["possible"],
        )
        .pivot(
            index="year",
            columns="month",
            values=sumvar,
        )
        .rename(
            columns=dict(enumerate(month_abbr[1:], start=1)),
        )
    )
    print(f"Observation Count For {station}")
    # Could not get pandas to output properly, so I manually do it :(
    for values in df.itertuples():
        print(values[0], end=" ")
        if sumvar in ["obs", "total_obs"]:
            print(" ".join(colorize(v, -1, 24 * 28) for v in values[1:]))
        else:
            print(" ".join(colorize(v, 1, 0.95) for v in values[1:]))


if __name__ == "__main__":
    main(sys.argv)
