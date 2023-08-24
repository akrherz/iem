"""
This application plots Flash Flood Guidance for
a time of your choice.  The time is used to query a 24 hour trailing window
to find the most recent FFG issuance.

<p>For dates after 1 Jan 2019, a gridded 5km analysis product is used as
the county guidance was discontinued. The raw data download option does
not work for that data either.  You can find the raw Grib files on the
IEM Archives, for example
<a href="https://mesonet.agron.iastate.edu/archive/data/2019/04/25/model/ffg/">
here</a>.
</p>

<p>Additionally, there is a <a
href="/api/1/docs#/default/ffg_bypoint_service_ffg_bypoint_json_get">
FFG by Point</a>
web service that provides the raw values.</p>

<p>For dates before 1 Jan 2019, this dataset is based on IEM processing
of county/zone based FFG guidance found in the FFG text products.
"""
import datetime
import os
from zoneinfo import ZoneInfo

import pandas as pd
import pygrib
from metpy.units import masked_array, units
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import SECTORS_NAME
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

HOURS = {
    "1": "One Hour",
    "3": "Three Hour",
    "6": "Six Hour",
    "12": "Twelve Hour",
    "24": "Twenty Four Hour",
}
PDICT = {
    "cwa": "Plot by NWS Forecast Office",
    "state": "Plot by State",
}
PDICT.update(SECTORS_NAME)
PDICT3 = {
    "yes": "YES: Label/Plot Counties/Zones",
    "no": "NO: Do not Label Counties/Zones",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    now = datetime.datetime.utcnow()
    desc["arguments"] = [
        dict(
            type="select",
            name="t",
            default="state",
            options=PDICT,
            label="Select plot extent type:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO: (ignored if plotting state)",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State: (ignored if plotting wfo)",
        ),
        dict(
            type="select",
            name="hour",
            default="1",
            options=HOURS,
            label="Guidance Period:",
        ),
        dict(
            type="select",
            name="ilabel",
            default="yes",
            options=PDICT3,
            label="Overlay values / plot counties on map?",
        ),
        dict(
            type="datetime",
            name="ts",
            default=now.strftime("%Y/%m/%d %H%M"),
            label="Valid Time (UTC Timezone):",
            min="2003/01/01 0000",
        ),
        dict(
            type="cmap",
            name="cmap",
            default="gist_rainbow",
            label="Color Ramp:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ts = ctx["ts"].replace(tzinfo=ZoneInfo("UTC"))
    hour = int(ctx["hour"])
    ilabel = ctx["ilabel"] == "yes"
    plot = MapPlot(
        apctx=ctx,
        sector=ctx["t"],
        continentalcolor="white",
        state=ctx["state"],
        cwa=ctx["wfo"],
        title=(
            f"NWS RFC {hour} Hour Flash Flood Guidance "
            f"on {ts:%-d %b %Y %H} UTC"
        ),
        subtitle=(
            "Estimated amount of %s Rainfall "
            "needed for non-urban Flash Flooding to commence"
        )
        % (HOURS[ctx["hour"]],),
        nocaption=True,
    )
    cmap = get_cmap(ctx["cmap"])
    bins = [
        0.01,
        0.6,
        0.8,
        1.0,
        1.2,
        1.4,
        1.6,
        1.8,
        2.0,
        2.25,
        2.5,
        2.75,
        3.0,
        3.5,
        4.0,
        5.0,
    ]
    if ts.year < 2019:
        column = "hour%02i" % (hour,)
        with get_sqlalchemy_conn("postgis") as conn:
            df = pd.read_sql(
                """
            WITH data as (
                SELECT ugc, rank() OVER (PARTITION by ugc ORDER by valid DESC),
                hour01, hour03, hour06, hour12, hour24
                from ffg WHERE valid >= %s and valid <= %s)
            SELECT *, substr(ugc, 3, 1) as ztype from data where rank = 1
            """,
                conn,
                params=(ts - datetime.timedelta(hours=24), ts),
                index_col="ugc",
            )
        df2 = df[df["ztype"] == "C"]
        plot.fill_ugcs(
            df2[column].to_dict(),
            bins=bins,
            cmap=cmap,
            plotmissing=False,
            ilabel=ilabel,
        )
        df2 = df[df["ztype"] == "Z"]
        plot.fill_ugcs(
            df2[column].to_dict(),
            bins=bins,
            cmap=cmap,
            plotmissing=False,
            units="inches",
            ilabel=ilabel,
        )
    else:
        # use grib data
        ts -= datetime.timedelta(hours=(ts.hour % 6))
        ts = ts.replace(minute=0)
        fn = None
        for offset in range(0, 24, 4):
            ts2 = ts - datetime.timedelta(hours=offset)
            testfn = ts2.strftime(
                "/mesonet/ARCHIVE/data/%Y/%m/%d/"
                "model/ffg/5kmffg_%Y%m%d%H.grib2"
            )
            if os.path.isfile(testfn):
                fn = testfn
                break
        if fn is None:
            raise NoDataFound("No valid grib data found!")
        grbs = pygrib.index(fn, "stepRange")
        grb = grbs.select(stepRange="0-%s" % (hour,))[0]
        lats, lons = grb.latlons()
        data = (
            masked_array(grb.values, data_units=units("mm"))
            .to(units("inch"))
            .m
        )
        plot.pcolormesh(lons, lats, data, bins, cmap=cmap)
        if ilabel:
            plot.drawcounties()
        df = pd.DataFrame()
    return plot.fig, df


if __name__ == "__main__":
    plotter({})
