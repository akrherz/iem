"""
The IEM attempts to create areal averaged climate values akin to what NCEI has
with its "Climdiv" dataset.  This autoplot creates comparisons between the two.

<p>Variances shown are problems with IEM's database/processing, not NCEI!
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import (
    get_autoplot_context,
    get_dbconn,
    get_properties,
    get_sqlalchemy_conn,
)
from sqlalchemy import text

PDICT = {
    "sum_precip": "Total Precipitation",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
}
MDICT = {
    "all": "Entire Year",
    "spring": "Spring (MAM)",
    "summer": "Summer (JJA)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
SDICT = {}  # to be filled


def fill_sdict():
    """Ensure we have stations to select from!"""
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name from stations where network ~* 'CLIMATE' and
        (substr(id, 3, 4) = '0000' or substr(id, 3, 1) = 'C') ORDER by id ASC
        """
    )
    for row in cursor:
        SDICT[row[0]] = f"[{row[0]}] {row[1]}"


def get_description():
    """Return a dict describing how to call this plotter"""
    fill_sdict()
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        {
            "type": "select",
            "options": SDICT,
            "name": "station",
            "default": "IA0000",
            "label": "Select statewide/climate district to compare:",
        },
        dict(
            type="select",
            name="m",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        {
            "type": "select",
            "options": PDICT,
            "default": "sum_precip",
            "label": "Which variable",
            "name": "varname",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    fill_sdict()
    ctx = get_autoplot_context(fdict, get_description())
    procdate = get_properties().get("ncei.climdiv.procdate", "20230101")

    station = ctx["station"]
    varname = ctx["varname"]
    sql = """
        with iem as (
            SELECT
            year, month,
            sum(precip) as iem_sum_precip, avg(high) as iem_avg_high,
            avg(low) as iem_avg_low
            from alldata WHERE station = :station
            GROUP by year, month
        ), ncei as (
            SELECT
            extract(year from day)::int as ncei_year,
            extract(month from day)::int as ncei_month,
            precip as ncei_sum_precip, high as ncei_avg_high,
            low as ncei_avg_low
            from ncei_climdiv WHERE station = :station
        )
        select n.*, i.* from ncei n JOIN iem i on
        (n.ncei_year = i.year and n.ncei_month = i.month)
        ORDER by i.year ASC, i.month ASC
    """
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(sql),
            conn,
            params={"station": station},
            index_col="year",
        )

    if df.empty:
        raise NoDataFound("Sorry, no data found!")

    month = ctx["m"]
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "winter":
        months = [12, 1, 2]
        df = df.reset_index()
        df["year"] = df.loc[df["month"].isin([1, 2]), "year"] - 1
        df = df.set_index("year")
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    df = (
        df.loc[df["month"].isin(months)]
        .groupby("year")
        .agg(
            {
                "ncei_sum_precip": "sum",
                "ncei_avg_high": "mean",
                "ncei_avg_low": "mean",
                "iem_sum_precip": "sum",
                "iem_avg_high": "mean",
                "iem_avg_low": "mean",
            }
        )
    )

    fig = figure(
        title=f"{SDICT[station]}:: [{MDICT[month]}] Bias (IEM minus NCEI)",
        subtitle=f"{PDICT[varname]}, NCEI processdate: {procdate}",
        apctx=ctx,
    )
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.8])
    df["iem_bias"] = df[f"iem_{varname}"] - df[f"ncei_{varname}"]
    bias = df["iem_bias"].mean()
    ax.bar(
        df.index.values,
        df["iem_bias"].values,
    )
    ax.set_ylabel(
        "Precipitation Bias [inch]"
        if varname == "sum_precip"
        else "Temperature Bias [F]"
    )
    ax.axhline(bias, lw=3, color="r")
    ax.text(
        df.index.values[-1] + 5,
        bias + 0.05,
        f"{bias:.2f}",
        color="r",
        ha="left",
    )
    ax.grid()

    y = 0.9
    fig.text(0.75, y, "Top 10 IEM > NCEI")
    y -= 0.035
    sdf = df.sort_values("iem_bias", ascending=False)
    for year, row in sdf.head(10).iterrows():
        iem = row[f"iem_{varname}"]
        ncei = row[f"ncei_{varname}"]
        fig.text(
            0.75,
            y,
            f"{year}  {iem:5.02f} {ncei:5.02f} {row['iem_bias']:5.02f}",
        )
        y -= 0.035

    y -= 0.035
    fig.text(0.75, y, "Top 10 IEM < NCEI")
    y -= 0.035

    for year, row in sdf.iloc[::-1].head(10).iterrows():
        iem = row[f"iem_{varname}"]
        ncei = row[f"ncei_{varname}"]
        fig.text(
            0.75,
            y,
            f"{year}  {iem:5.02f} {ncei:5.02f} {row['iem_bias']:5.02f}",
        )
        y -= 0.035

    return fig, df


if __name__ == "__main__":
    plotter({})
