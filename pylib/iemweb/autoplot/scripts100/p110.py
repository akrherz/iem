"""
This plot presents the weekly percentage of
precipitation events within a given rainfall bin.
"""

from calendar import month_abbr
from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION

CWEEK = {
    1: "3/1-->3/7   ",
    2: "3/8-->3/14  ",
    3: "3/15-->3/21 ",
    4: "3/22-->3/28 ",
    5: "3/29-->4/4  ",
    6: "4/5-->4/11  ",
    7: "4/12-->4/18 ",
    8: "4/19-->4/25 ",
    9: "4/26-->5/2  ",
    10: "5/3-->5/9   ",
    11: "5/10-->5/16 ",
    12: "5/17-->5/23 ",
    13: "5/24-->5/30 ",
    14: "5/31-->6/6  ",
    15: "6/7-->6/13  ",
    16: "6/14-->6/20 ",
    17: "6/21-->6/27 ",
    18: "6/28-->7/4  ",
    19: "7/5-->7/11  ",
    20: "7/12-->7/18 ",
    21: "7/19-->7/25 ",
    22: "7/26-->8/1  ",
    23: "8/2-->8/8   ",
    24: "8/9-->8/15  ",
    25: "8/16-->8/22 ",
    26: "8/23-->8/29 ",
    27: "8/30-->9/5  ",
    28: "9/6-->9/12  ",
    29: "9/13-->9/19 ",
    30: "9/20-->9/26 ",
    31: "9/27-->10/3 ",
    32: "10/4-->10/10",
    33: "10/11-->10/17",
    34: "10/18-->10/24",
    35: "10/25-->10/31",
    36: "11/1-->11/7 ",
    37: "11/8-->11/14",
    38: "11/15-->11/21",
    39: "11/22-->11/28",
    40: "11/29-->12/5",
    41: "12/6-->12/12",
    42: "12/13-->12/19",
    43: "12/20-->12/26",
    44: "12/27-->1/2 ",
    45: "1/3-->1/9   ",
    46: "1/10-->1/16 ",
    47: "1/17-->1/23 ",
    48: "1/24-->1/30 ",
    49: "1/31-->2/6  ",
    50: "2/7-->2/13  ",
    51: "2/14-->2/20 ",
    52: "2/21-->2/27 ",
    53: "2/28-->2/29 ",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    desc["arguments"] = [
        ARG_STATION,
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        with events as (
            SELECT c.climoweek, a.precip, a.year from alldata_{station[:2]} a
            JOIN climoweek c on (c.sday = a.sday) WHERE a.station = %s
            and precip > 0.009),
        ranks as (
            SELECT climoweek, year,
            rank() OVER (
                PARTITION by climoweek ORDER by precip DESC, year DESC)
            from events),
        stats as (
        SELECT climoweek, max(precip), avg(precip),
        sum(case when precip > 0.009 and precip < 0.26 then 1 else 0 end)
            as cat1,
        sum(case when precip >= 0.26 and precip < 0.51 then 1 else 0 end)
            as cat2,
        sum(case when precip >= 0.51 and precip < 1.01 then 1 else 0 end)
            as cat3,
        sum(case when precip >= 1.01 and precip < 2.01 then 1 else 0 end)
            as cat4,
        sum(case when precip >= 2.01 then 1 else 0 end) as cat5,
        sum(case when precip > 0.009 and precip < 0.26 then precip else 0 end)
            as sum_cat1,
        sum(case when precip >= 0.26 and precip < 0.51 then precip else 0 end)
            as sum_cat2,
        sum(case when precip >= 0.51 and precip < 1.01 then precip else 0 end)
            as sum_cat3,
        sum(case when precip >= 1.01 and precip < 2.01 then precip else 0 end)
            as sum_cat4,
        sum(case when precip >= 2.01 then precip else 0 end) as sum_cat5,
        count(*) from events GROUP by climoweek)
        SELECT e.*, r.year from
        stats e JOIN ranks r on (r.climoweek = e.climoweek) WHERE r.rank = 1
        ORDER by e.climoweek ASC
        """,
            conn,
            params=(station,),
            index_col="climoweek",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    bins = {
        1: "0.01 - 0.25",
        2: "0.26 - 0.50",
        3: "0.51 - 1.00",
        4: "1.01 - 2.00",
        5: "2.01 +",
    }
    today = date.today()
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {today:%d %b %Y}\n"
        "# Climate Record: "
        f"{ctx['_nt'].sts[station]['archive_begin']} -> {today}\n"
        f"# Site Information: {ctx['_sname']}\n"
        "# Contact Information: "
        "Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
        "# Based on climoweek periods, this report summarizes liquid "
        "precipitation.\n"
        "#                                     Number of precip events - "
        "(% of total)\n"
        " CL                MAX         MEAN   0.01-    0.26-    0.51-    "
        "1.01-            TOTAL\n"
        " WK TIME PERIOD    VAL  YR     RAIN     0.25     0.50     1.00     "
        "2.00    >2.01  DAYS\n"
    )
    title = f"{ctx['_sname']}:: Precipitation Bin [inch] Frequency Histogram"
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes((0.1, 0.15, 0.8, 0.75))
    df["total"] = (
        df["cat1"] + df["cat2"] + df["cat3"] + df["cat4"] + df["cat5"]
    )
    for i in range(1, 6):
        df[f"cat{i}f"] = df[f"cat{i}"] / df["total"] * 100.0
    cs = df[["cat1f", "cat2f", "cat3f", "cat4f", "cat5f"]].cumsum(axis=1)
    cs["cat0f"] = 0
    # Reset xaxis to make it prettier
    cs = (
        cs.assign(
            x=lambda df_: np.where(
                df_.index.values > 44,
                df_.index.values - 45,
                df_.index.values + 9,
            ),
            cat1=df["cat1f"],
            cat2=df["cat2f"],
            cat3=df["cat3f"],
            cat4=df["cat4f"],
            cat5=df["cat5f"],
        )
        .sort_values("x", ascending=True)
        .drop(53, errors="ignore")
    )
    for i in range(1, 6):
        # We fake a x-axis to remove the weird start on Mar 1 thing
        ax.bar(
            np.arange(0, len(cs.index)) * 7,
            cs[f"cat{i}"].values,
            bottom=cs[f"cat{i-1}f"].values,
            label=bins[i],
            width=7.0,
        )
    ax.grid(True)
    ax.legend(ncol=5, loc=(0.1, -0.15))
    ax.set_ylabel("Daily Frequency of Precip Bin by Climoweek [%]")
    ax.set_xlabel("Groupted by Climoweek of Year")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_xlim(-0.5, 358.5)

    annEvents = 0
    cat1t = 0
    cat2t = 0
    cat3t = 0
    cat4t = 0
    cat5t = 0
    maxRain = 0
    totRain = 0
    for cw, row in df.iterrows():
        cat1 = row["cat1"]
        cat2 = row["cat2"]
        cat3 = row["cat3"]
        cat4 = row["cat4"]
        cat5 = row["cat5"]
        cat1t += cat1
        cat2t += cat2
        cat3t += cat3
        cat4t += cat4
        cat5t += cat5
        maxval = row["max"]
        if maxval > maxRain:
            maxRain = maxval
        meanval = row["avg"]
        annEvents += row["total"]
        totRain += row["total"] * meanval

        res += (
            "%3s %-13s %5.2f %i   %4.2f %4i(%2i) %4i(%2i) "
            "%4i(%2i) %4i(%2i) %4i(%2i)   %4i\n"
        ) % (
            cw,
            CWEEK[cw],
            maxval,
            row["year"],
            meanval,
            cat1,
            round((float(cat1) / float(row["total"])) * 100.0),
            cat2,
            round((float(cat2) / float(row["total"])) * 100.0),
            cat3,
            round((float(cat3) / float(row["total"])) * 100.0),
            cat4,
            round((float(cat4) / float(row["total"])) * 100.0),
            cat5,
            round((float(cat5) / float(row["total"])) * 100.0),
            row["total"],
        )

    res += (
        "%-17s %5.2f        %4.2f %4i(%2i) %4i(%2i) "
        "%4i(%2i) %4i(%2i) %4i(%2i)  %5i\n"
    ) % (
        "ANNUAL TOTALS",
        maxRain,
        totRain / float(annEvents),
        cat1t,
        (float(cat1t) / float(annEvents)) * 100,
        cat2t,
        (float(cat2t) / float(annEvents)) * 100,
        cat3t,
        (float(cat3t) / float(annEvents)) * 100,
        cat4t,
        (float(cat4t) / float(annEvents)) * 100,
        cat5t,
        (float(cat5t) / float(annEvents)) * 100,
        annEvents,
    )

    return fig, df, res
