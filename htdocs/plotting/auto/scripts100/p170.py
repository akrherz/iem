"""METAR frequency"""
import calendar
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("TS", "All Thunder Reports (TS)"),
        ("VCTS", "Thunder in Vicinity (VCTS)"),
        ("1", "Thunder Reports (excluding VCTS)"),
        ("-SN", "Light Snow (-SN)"),
        ("PSN", "Heavy Snow (+SN)"),  # +SN causes CGI issues
        ("FZFG", "Freezing Fog (FZFG)"),
        ("FZRA", "Freezing Rain (FZRA)"),
        ("FG", "Fog (FG)"),
        ("BLSN", "Blowing Snow (BLSN)"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart totals the number of distinct calendar
    days per month that a given present weather condition is reported within
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
    </ul>
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
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
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
    df = read_sql(
        f"""
    WITH data as (
        SELECT distinct date(valid at time zone %s) from alldata
        where station = %s and {limiter}
        and valid > '1973-01-01' and report_type = 2)

    SELECT extract(year from date)::int as year,
    extract(month from date)::int as month,
    count(*) from data GROUP by year, month ORDER by year, month
    """,
        pgconn,
        params=(tzname, station),
        index_col=None,
    )

    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")
    (fig, ax) = plt.subplots(1, 1)
    ax.set_title(
        (
            "[%s] %s %s Events\n"
            "(%s-%s) Distinct Calendar Days with '%s' Reported"
        )
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            PDICT[pweather],
            syear,
            datetime.date.today().year,
            pweather if pweather != "1" else "TS",
        )
    )
    df2 = df[df["year"] == year]
    if not df2.empty:
        ax.bar(
            df2["month"].values - 0.2,
            df2["count"].values,
            width=0.4,
            fc="r",
            ec="r",
            label="%s" % (year,),
        )
    df2 = df.groupby("month").sum()
    years = (datetime.date.today().year - syear) + 1
    yvals = df2["count"] / years
    ax.bar(
        df2.index.values + 0.2, yvals, width=0.4, fc="b", ec="b", label="Avg"
    )
    for x, y in zip(df2.index.values, yvals):
        ax.text(x, y + 0.2, "%.1f" % (y,))
    ax.set_xlim(0.5, 12.5)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_ylabel("Days Per Month")
    ax.set_ylim(top=(ax.get_ylim()[1] + 2))
    ax.legend(loc="best")
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(dict(zstation="ALO", year=2017, var="FG", network="IA_ASOS"))
