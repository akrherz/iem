"""
The IEM attempts to create areal averaged climate values akin to what NCEI has
with its "Climdiv" dataset.  This autoplot creates comparisons between the two.

<p>Variances shown are problems with IEM's database/processing, not NCEI!
"""
import datetime

import pandas as pd
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import (
    get_autoplot_context,
    get_properties,
    get_sqlalchemy_conn,
)
from sqlalchemy import text

PDICT = {
    "sum_precip": "Total Precipitation",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select state to compare",
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
    ctx = get_autoplot_context(fdict, get_description())
    procdate = get_properties().get("ncei.climdiv.procdate", "20230101")
    threshold = datetime.datetime.strptime(procdate, "%Y%m%d").replace(day=1)

    state = ctx["state"]
    varname = ctx["varname"]
    sql = """
        with iem as (
            SELECT
            year,
            sum(precip) as iem_sum_precip, avg(high) as iem_avg_high,
            avg(low) as iem_avg_low
            from alldata WHERE station = :station and day < :threshold
            GROUP by year
        ), ncei as (
            SELECT
            extract(year from day)::int as ncei_year,
            sum(precip) as ncei_sum_precip, avg(high) as ncei_avg_high,
            avg(low) as ncei_avg_low
            from ncei_climdiv WHERE station = :station GROUP by ncei_year
        )
        select n.*, i.* from ncei n JOIN iem i on (n.ncei_year = i.year)
        ORDER by i.year ASC
    """
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(sql),
            conn,
            params={"station": f"{state}0000", "threshold": threshold},
            index_col="year",
        )

    if df.empty:
        raise NoDataFound("Sorry, no data found!")

    fig = figure(
        title=f"{reference.state_names[state]} Yearly Bias (IEM minus NCEI)",
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
    ax.set_ylabel("Precipitation Bias [inch]")
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
