"""METAR frequency"""
import calendar
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "TS": "All Thunder Reports (TS)",
    "VCTS": "Thunder in Vicinity (VCTS)",
    "1": "Thunder Reports (excluding VCTS)",
    "-SN": "Light Snow (-SN)",
    "PSN": "Heavy Snow (+SN)",  # +SN causes CGI issues
    "SN": "Any Snow (*SN*)",
    "TSPL": "Thunder and Ice Pellets (TSPL)",
    "TSSN": "Thunder and Snow (TSSN)",
    "FZFG": "Freezing Fog (FZFG)",
    "FZRA": "Freezing Rain (FZRA)",
    "TSFZRA": "Thunder and Freezing Rain (TSFZRA)",
    "FG": "Fog (FG)",
    "BLSN": "Blowing Snow (BLSN)",
    "FU": "Smoke (FU)",
}
PDICT2 = {
    "day": "Count Distinct Days per Month per Year",
    "hour": "Count Distinct Hours per Month per Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart totals the number of distinct calendar
    days or hours per month that a given present weather condition is reported within
    the METAR data feed.  The calendar day is computed for the local time zone
    of the reporting station.

    <p>The reporting of present weather codes within METARs has changed over
    the years and there is some non-standard nomenclature used by some sites.
    The thunder (TS) reports are delineated into three categories here to
    hopefully allow more accurate statistics.
    <ul>
      <li><strong>All Thunder Reports (TS)</strong> includes any
      <code>TS</code> mention in any present weather code</li>
      <li><strong>Thunder in Vicinity (VCTS)</strong> includes any
      <code>VCTS</code> mention in any present weather code, for example,
      <code>VCTSRA</code> would match.</li>
      <li><strong>Thunder Reports (excluding VCTS)</strong> includes most
      <code>TS</code> mentions, but not any including <code>VC</code></li>
    </ul></p>

    <p>This autoplot considers both routine and special hourly reports.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="year",
            name="year",
            label="Year to Highlight:",
            default=datetime.date.today().year,
            min=1973,
        ),
        dict(
            type="select",
            name="var",
            default="FG",
            label="Present Weather Option:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="w",
            default="day",
            label="How to aggregate the data:",
            options=PDICT2,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    year = ctx["year"]
    pweather = ctx["var"]
    if pweather == "PSN":
        pweather = "+SN"
        PDICT["+SN"] = PDICT["PSN"]

    tzname = ctx["_nt"].sts[station]["tzname"]
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    syear = max([1973, ab.year])
    limiter = "array_to_string(wxcodes, '') LIKE '%%" + pweather + "%%'"
    if pweather == "1":
        # Special in the case of non-VCTS
        limiter = (
            "ARRAY['TS'::varchar, '-TSRA'::varchar, 'TSRA'::varchar, "
            "'-TS'::varchar, '+TSRA'::varchar, '+TSSN'::varchar,"
            "'-TSSN'::varchar, '-TSDZ'::varchar] && wxcodes"
        )
    trunc = "day" if ctx["w"] == "day" else "hour"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            f"""
        WITH data as (
            SELECT distinct date_trunc(%s,
                valid at time zone %s + '10 minutes'::interval) as datum
            from alldata where station = %s and {limiter}
            and valid > '1973-01-01' and report_type != 1)

        SELECT extract(year from datum)::int as year,
        extract(month from datum)::int as month,
        count(*) from data GROUP by year, month ORDER by year, month
        """,
            conn,
            params=(trunc, tzname, station),
            index_col=None,
        )

    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")
    t1 = "Calendar Dates" if ctx["w"] == "day" else "Hourly Observations"
    t2 = pweather if pweather != "1" else "TS"
    t3 = " with at least one hourly report" if ctx["w"] == "day" else ""
    title = (
        f"{ctx['_sname']}:: {PDICT[pweather]} "
        "Events\n"
        f"({syear}-{datetime.date.today().year}) Distinct {t1} with "
        f"'{t2}' Reported{t3}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    df2 = df[df["year"] == year]
    if not df2.empty:
        ax.bar(
            df2["month"].values - 0.2,
            df2["count"].values,
            width=0.4,
            fc="r",
            ec="r",
            label=f"{year}",
        )
        for x, y in zip(df2["month"].values, df2["count"].values):
            ax.text(x - 0.2, y + 0.2, f"{y:.0f}", ha="center")
    df2 = df.groupby("month").sum()
    years = (datetime.date.today().year - syear) + 1
    yvals = df2["count"] / years
    ax.bar(
        df2.index.values + 0.2, yvals, width=0.4, fc="b", ec="b", label="Avg"
    )
    for x, y in zip(df2.index.values, yvals):
        ax.text(x + 0.2, y + 0.2, f"{y:.1f}", ha="center")
    ax.set_xlim(0.5, 12.5)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    t1 = "Days" if ctx["w"] == "day" else "Hours"
    ax.set_ylabel(f"{t1} Per Month")
    ax.set_ylim(top=(ax.get_ylim()[1] + 2))
    ax.legend(loc="best")
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(dict(zstation="ALO", year=2017, var="TSFZRA", network="IA_ASOS"))
