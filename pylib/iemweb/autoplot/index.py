"""IEM Autoplot Frontend.

IEM_APPID 92
"""

import calendar
import os
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
from paste.request import get_cookie_dict
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import BadWebRequest
from pyiem.htmlgen import make_select, station_select
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE
from pyiem.reference import SECTORS_NAME, state_names
from pyiem.templates.iem import TEMPLATE
from pyiem.util import LOG, html_escape, utc
from pyiem.webutil import ensure_list, iemapp

from iemweb.autoplot import FEMA_REGIONS
from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot.meta import get_metadict

sn_contig = state_names.copy()
for _sn in "AK HI PR VI GU AS MP".split():
    sn_contig.pop(_sn, None)
NETWORK_RE = re.compile(r"^[A-Z0-9_\-]+$")
DATE_RE = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})$")
SDAY_RE = re.compile(r"^(\d{2})(\d{2})$")
DATETIME_RE = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2}) (\d{1,2})(\d{2})$")
HIGHCHARTS = "12.1.2"
OPENLAYERS = "7.5.1"
CSECTORS = state_names.copy()
CSECTORS.update(SECTORS_NAME)
CMAPS = {
    "Perceptually Uniform Sequential": [
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
    ],
    "Sequential": [
        "Greys",
        "Purples",
        "Blues",
        "Greens",
        "Oranges",
        "Reds",
        "YlOrBr",
        "YlOrRd",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ],
    "Sequential (2)": [
        "binary",
        "gist_yarg",
        "gist_gray",
        "gray",
        "bone",
        "pink",
        "spring",
        "summer",
        "autumn",
        "winter",
        "cool",
        "Wistia",
        "hot",
        "afmhot",
        "gist_heat",
        "copper",
    ],
    "Diverging": [
        "PiYG",
        "PRGn",
        "BrBG",
        "PuOr",
        "RdGy",
        "RdBu",
        "RdYlBu",
        "RdYlGn",
        "Spectral",
        "coolwarm",
        "bwr",
        "seismic",
        "berlin",
        "managua",
        "vanimo",
    ],
    "Cyclic": [
        "twilight",
        "twilight_shifted",
        "hsv",
    ],
    "Qualitative": [
        "Pastel1",
        "Pastel2",
        "Paired",
        "Accent",
        "Dark2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
    ],
    "Miscellaneous": [
        "flag",
        "prism",
        "ocean",
        "gist_earth",
        "terrain",
        "gist_stern",
        "gnuplot",
        "gnuplot2",
        "CMRmap",
        "cubehelix",
        "brg",
        "gist_rainbow",
        "rainbow",
        "jet",
        "turbo",
        "nipy_spectral",
        "gist_ncar",
    ],
}


def map_select_widget(network, name):
    """Generate the HTML for a wiz bang popup."""
    return f"""
&nbsp; <button type="button" id="button_{network}_{name}" data-state="0"
onClick="mapFactory('{network}', '{name}');">Show Map</button>
<div style="display: none; width: 100%; height: 640px;"
 id="map_{network}_{name}_wrap">
<br />Click dot to select in form above. <strong>Key</strong>
<img src="/images/green_dot.svg" style="height: 15px;"> Online &nbsp;
<img src="/images/red_dot.svg" style="height: 15px;"> Offline<br />
<div style="width: 100%; height: 600px;" id="map_{network}_{name}"></div>
</div>
<div class="popup" id="popup_{network}_{name}" style="display: none;"></div>
"""


def networkselect_handler(value: str, arg: dict, res: dict) -> str:
    """Select a station from a given network."""
    if not isinstance(arg["network"], list):
        res["pltvars"].append(f"network:{arg['network']}")
    if not NETWORK_RE.match(value):
        raise BadWebRequest("Invalid network provided")
    return station_select(
        arg["network"],
        value,
        arg["name"],
        select_all=arg.get("all", False),
    ) + map_select_widget(arg["network"], arg["name"])


def station_handler(value, arg: dict, fdict, res, typ: str):
    """Generate HTML."""
    networks = {}
    netlim = ""
    if typ == "zstation":
        netlim = "WHERE id ~* 'ASOS'"
    elif typ == "station":
        netlim = "WHERE id ~* 'CLIMATE'"
    elif typ == "sid" and not arg.get("include_climodat", False):
        netlim = "WHERE id !~* 'CLIMATE'"
    with get_sqlalchemy_conn("mesosite") as conn:
        dbres = conn.execute(
            sql_helper(
                "SELECT id, name from networks {netlim} ORDER by name ASC",
                netlim=netlim,
            )
        )
        for row in dbres:
            networks[row[0]] = row[1]
    # We could have two plus zstations
    networkcgi = "network"
    if arg["name"][-1].isdigit():
        networkcgi += arg["name"][-1]
    # get the default network set with this autoplot
    network = arg.get("network", "IA_ASOS")
    network = html_escape(fdict.get(networkcgi, network))
    if not NETWORK_RE.match(network):
        raise BadWebRequest("Invalid network provided")
    netselect = make_select(
        networkcgi, network, networks, jscallback="onNetworkChange"
    )
    select = station_select(network, value, arg["name"])
    res["pltvars"].append(f"{networkcgi}:{network}")
    return netselect + " " + select + map_select_widget(network, arg["name"])


def ugc_select(state: str, ugc: str) -> str:
    """Generate a select for a given state."""
    sql = """
    with data as (
        select ugc, case when end_ts is not null then
        to_char(begin_ts, 'YYYY-mm-dd') || '-' || to_char(end_ts, 'YYYY-mm-dd')
        else null end as rng, name,
        row_number() OVER (PARTITION by ugc ORDER by end_ts nulls first)
        from ugcs where substr(ugc, 1, 2) = :state)
    select ugc, name, rng from data where row_number = 1
    order by name asc, ugc asc
    """
    ar = {}
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(sql_helper(sql), {"state": state})
        for row in res:
            name = f"{row[1]} {'(Zone)' if row[0][2] == 'Z' else ''}"
            if row[2] is not None:
                name += f" {row[2]}"
            ar[row[0]] = name
    return make_select("ugc", ugc, ar, cssclass="iemselect2")


def ugc_handler(name, value, fdict):
    """Handle selection of UGCs."""
    privfield = f"_{name}_state"
    state = fdict.get(privfield, "IA")
    state_select = make_select(
        privfield, state, state_names, jscallback="onNetworkChange"
    )
    return state_select + " " + ugc_select(state, value)


def vtec_ps_handler(fdict, arg):
    """Handle VTEC Phenomena + Significance."""
    suffix = arg["name"]
    default_p, default_s = arg["default"].split(".")
    value = html_escape(fdict.get(f"phenomena{suffix}", default_p))
    s = make_select(f"phenomena{suffix}", value, VTEC_PHENOMENA)
    value = html_escape(fdict.get(f"significance{suffix}", default_s))
    s += make_select(f"significance{suffix}", value, VTEC_SIGNIFICANCE)
    return s


def cmap_handler(fdict, value, arg, res):
    """Our fancy pants cmap handler."""
    reverse_on = fdict.get(f"{arg['name']}_r", "off") == "on"
    if value.endswith("_r"):
        value = value.replace("_r", "")
        reverse_on = True
    s = make_select(
        arg["name"],
        value,
        CMAPS,
        cssclass="cmapselect form-control-lg",
        showvalue=False,
    )
    checked = ' checked="checked"' if reverse_on else ""
    s += (
        f'&nbsp; <input type="checkbox" name="{arg["name"]}_r" '
        f'value="on"{checked}> Reverse Colormap?'
    )
    res["pltvars"].append(f"{arg['name']}:{value}{'_r' if reverse_on else ''}")
    return s


def datetypes_handler(arg, value):
    """Handle simple forms."""
    value = int(value)
    if arg["type"] == "month":
        items = zip(range(1, 13), calendar.month_name[1:], strict=False)
    elif arg["type"] in ["zhour", "hour"]:
        fmt = "%I %p" if arg["type"] == "hour" else "%H Z"
        items = zip(
            range(24),
            [utc(2000, 1, 1, hr).strftime(fmt) for hr in range(24)],
            strict=True,
        )
    elif arg["type"] == "day":
        items = zip(range(1, 32), range(1, 32), strict=False)
    else:
        vmin = arg.get("min", 1893)
        vmax = arg.get("max", utc().year)
        if value > (vmax + 1) or value < vmin:
            raise ValueError("Year value out of range")
        items = zip(range(vmin, vmax + 1), range(vmin, vmax + 1), strict=True)
    return make_select(arg["name"], value, dict(items), showvalue=False)


def sday_handler(value: str, arg: dict):
    """Handler for datetime instances."""
    dpname = f"datepicker_{arg['name']}"
    vmin = arg.get("min", "0101")
    vmax = arg.get("max", "1231")
    # account for legacy URLs that had dates here
    if value.find("/") > -1:
        value = f"{value[5:7]}{value[8:10]}"
    if not SDAY_RE.match(value):
        raise BadWebRequest("Invalid sdate format")

    return (
        f'<input type="text" id="{dpname}" autocomplete="off" class="apfp" '
        f'name="{arg["name"]}" '
        f'data-defaultDate="{value}" '
        f'data-minDate="{vmin}" '
        f'data-maxDate="{vmax}" '
        'data-sday="true" data-dateFormat="md">(mmdd)'
    )


def date_handler(value: str, arg: dict):
    """Handler for datetime instances."""
    dpname = f"datepicker_{arg['name']}"
    vmin = arg.get("min", "1893/1/1")
    vmax = arg.get("max", utc().strftime("%Y/%m/%d"))

    def _ymd(val: str):
        rectified = val.replace("-", "/")
        if not DATE_RE.match(rectified):
            raise BadWebRequest("Invalid date format")
        parts = [int(x) for x in rectified.split("/")]
        return f"{parts[0]:04d}/{parts[1]:02d}/{parts[2]:02d}"

    return (
        f'<input type="text" name="{arg["name"]}" id="{dpname}" '
        'class="apfp" data-dateFormat="Y/m/d" '
        f'data-defaultDate="{_ymd(value)}" value="{_ymd(value)}" '
        f'data-minDate="{_ymd(vmin)}" data-maxDate="{_ymd(vmax)}" '
        f'autocomplete="off"> (YYYY/mm/dd)'
    )


def datetime_handler(value, arg):
    """Handler for datetime instances."""
    dpname = f"fp_{arg['name']}"
    vmax = arg.get("max", utc().strftime("%Y/%m/%d %H%M"))
    vmin = arg.get("min", "1893/01/01 0000")

    # Convert to flatpickr format: Y/m/d H:i
    def _to_fp(val):
        # Accepts 'YYYY/MM/DD HHmm' or 'YYYY-MM-DD HHmm'
        if val is None or val == "":
            raise BadWebRequest("Invalid datetime value")
        dt = val.replace("-", "/").split()
        datepart = dt[0]
        timepart = dt[1] if len(dt) > 1 else "0000"
        if not DATETIME_RE.match(f"{datepart} {timepart}"):
            raise BadWebRequest("Invalid datetime format")
        y, m, d = [int(x) for x in datepart.split("/")]
        h, mi = int(timepart[:2]), int(timepart[2:])
        return f"{y:04d}-{m:02d}-{d:02d} {h:02d}{mi:02d}"

    return (
        f'<input type="text" name="{arg["name"]}" id="{dpname}" class="apfp" '
        'data-enableTime="true" data-dateFormat="Y/m/d Hi" '
        f'data-defaultDate="{_to_fp(value)}" '
        f'data-minDate="{_to_fp(vmin)}" data-maxDate="{_to_fp(vmax)}" '
        'data-allowInput="true" data-time24hr="true" '
        'autocomplete="off"> (YYYY/mm/dd HH24MI)'
    )


def add_to_plotvars(value, fdict, arg, res):
    """Add to our plotvars."""
    if value == "":
        return
    if arg["type"] == "vtec_ps":
        suffix = arg["name"]
        value = html_escape(fdict.get(f"phenomena{suffix}", "SV"))
        res["pltvars"].append(f"phenomena{suffix}:{value}")
        value = html_escape(fdict.get(f"significance{suffix}", "W"))
        res["pltvars"].append(f"significance{suffix}:{value}")
        return
    if arg["type"] == "cmap":
        return
    if isinstance(value, str | int | float):
        res["pltvars"].append(f"{arg['name']}:{value}")
    elif isinstance(value, date):
        res["pltvars"].append(f"{arg['name']}:{value.strftime('%Y-%m-%d')}")
    elif isinstance(value, datetime):
        res["pltvars"].append(
            f"{arg['name']}:{value.strftime('%Y-%m-%d %H%M')}"
        )
    else:
        for val in value:
            res["pltvars"].append(f"{arg['name']}:{val}")


def set_cookie_networkselect(cookies, headers, arg, value):
    """Set a cookie with special logic for how stations are handled."""
    network = arg.get("network", "")
    name = f"{arg['name']}_{network}"  # Important
    if value == cookies.get(name):
        return
    headers.append(
        (
            "Set-Cookie",
            f"{name}={value}; Path=/plotting/auto/; Max-Age=8640000",
        )
    )


def set_cookie(cookies, headers, name, value):
    """Optionally set a cookie in the response headers."""
    if value == cookies.get(name):
        return
    headers.append(
        (
            "Set-Cookie",
            f"{name}={value}; Path=/plotting/auto/; Max-Age=8640000",
        )
    )


def get_cookie_value(arg, cookies):
    """Some custom cruft here."""
    if arg["type"] in ["state", "csector"]:
        return cookies.get(arg["name"])
    if arg["type"] == "networkselect":
        return cookies.get(f"{arg['name']}_{arg['network']}")
    return None


def get_timing(apid):
    """Get a timing sample."""
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "SELECT avg(timing)::int from autoplot_timing where appid = %s "
        "and valid > (now() - '7 days'::interval)",
        (apid,),
    )
    timing = cursor.fetchone()["avg"]
    pgconn.close()
    return timing if timing is not None else -1


def compute_dat_label(attribs: dict) -> str:
    """This is suboptimal."""
    event_id = attribs.get("event_id", "")
    wfo = attribs.get("wfo", "")
    efscale = attribs.get("efscale", "")
    try:
        length = attribs.get("length")
    except ValueError:
        length = 0
    sts = pd.Timestamp(attribs.get("starttime") / 1000, unit="s", tz="UTC")
    return f"{wfo} {efscale} {event_id} {sts:%H%M}Z {length:.0f} miles"


def dat_handler(fdict, res):
    """Generate the Damage Assessment Tool form."""
    dt = fdict.get("dat", "2024/05/21")
    gid = fdict.get("datglobalid", "")
    # Ensure that gid looks like a guid
    if len(gid) != 38:
        gid = "{495DE596-B299-41FE-9C90-13C87E43FE0B}"
    res["pltvars"].append(f"datglobalid:{gid}")
    # Query DAT for the list of events
    ss = '<select name="datglobalid">\n'
    with httpx.Client() as client:
        sts = datetime.strptime(dt, "%Y/%m/%d").replace(tzinfo=ZoneInfo("UTC"))
        ets = sts + timedelta(hours=36)
        url = (
            "https://services.dat.noaa.gov/arcgis/rest/services/"
            "nws_damageassessmenttoolkit/DamageViewer/FeatureServer/1/query?"
            "f=json&returnGeometry=false&outFields=*&"
            "geometryType=esriGeometryPolyline&"
            f"time={sts:%s}000%2C{ets:%s}000"
        )
        datjson = client.get(url, timeout=30).json()
        for feat in datjson["features"]:
            _globalid = feat["attributes"]["globalid"]
            ss += (
                f'<option value="{_globalid}" '
                f"{'selected=' if _globalid == gid else ''}>"
                f"{compute_dat_label(feat['attributes'])} </option>\n"
            )
    ss += "</select>"
    return (
        f'<input type="text" name="dat" id="dat" autocomplete="off" '
        f'value="{dt}" '
        'class="apfp" data-enableTime="false" data-dateFormat="Y/m/d" '
        'data-allowInput="true" data-mindate="2001/01/01" data-onc="true" '
        f'data-defaultDate="{dt}" data-maxDate="{utc():%Y-%m-%d}"> '
        f"(YYYY/mm/dd) &nbsp; {ss}"
    )


def generate_form(apid, fdict, headers, cookies):
    """Generate out the form, oh boy!"""
    res = {
        "title": "IEM Autoplot",
        "nassmsg": "",
        "description": "",
        "imguri": f"/plotting/auto/plot/{apid}/",
        "pltvars": [],
        "formhtml": "",
        "image": "",
        "extrascripts": "",
        "headextra": "",
        "dataextra": "",
        "issues": "",
        "frontend": None,
    }
    if apid == 0:
        return res
    fmt = fdict.get("_fmt")
    # This should be instant, but the other end may be doing a thread
    # restart, which takes a bit of time.
    meta = get_metadict(int(apid))
    res["title"] = f"{apid}. {meta['title']}"
    res["frontend"] = meta.get("frontend")
    if meta.get("description"):
        res["description"] = (
            '<div class="alert alert-info"><h4>Plot Description:</h4>'
            f"{meta['description']}</div>"
        )
    if fmt is None:
        if meta.get("highcharts", False):
            fmt = "js"
        elif meta.get("report", False) and meta.get("nopng", False):
            fmt = "text"
        else:
            fmt = "png"
    if meta.get("nass") is not None:
        res["nassmsg"] = """
<p><div class="alert alert-warning">This data presentation utilizes the
        <a href="http://quickstats.nass.usda.gov/">USDA NASS Quickstats</a>.
        This presentation is not endorsed nor certified by USDA.
</div></p>
        """
    form = ""
    formhtml = ""
    for arg in meta["arguments"]:
        value = fdict.get(arg["name"], get_cookie_value(arg, cookies))
        if arg.get("multiple", False):
            value = ensure_list(fdict, arg["name"])
        if isinstance(value, str):
            value = html_escape(value)
            # Avoid situation of the Cookie having _ALL set and this form
            # entry not supporting _ALL
            if value == "_ALL" and not arg.get("all", False):
                value = None
        if value is None:
            value = str(arg["default"])
        if arg["type"] in ["zstation", "sid", "station"]:
            form = station_handler(value, arg, fdict, res, arg["type"])
        elif arg["type"] == "ugc":
            form = ugc_handler(arg["name"], value, fdict)
        elif arg["type"] == "networkselect":
            set_cookie_networkselect(cookies, headers, arg, value)
            form = networkselect_handler(value, arg, res)
        elif arg["type"] == "phenomena":
            form = make_select(arg["name"], value, VTEC_PHENOMENA)
        elif arg["type"] == "significance":
            form = make_select(arg["name"], value, VTEC_SIGNIFICANCE)
        elif arg["type"] == "vtec_ps":
            form = vtec_ps_handler(fdict, arg)
        elif arg["type"] == "state":
            sn = state_names if arg.get("contiguous") is None else sn_contig
            if value not in sn:
                value = "IA"
            form = make_select(arg["name"], value, sn)
        elif arg["type"] == "csector":
            set_cookie(cookies, headers, arg["name"], value)
            form = make_select(arg["name"], value, CSECTORS, showvalue=False)
        elif arg["type"] == "cmap":
            form = cmap_handler(fdict, value, arg, res)
        elif arg["type"] == "fema":
            form = make_select(arg["name"], value, FEMA_REGIONS)
        elif arg["type"] in ["text", "int", "float"]:
            form = (
                f'<input type="text" name="{arg["name"]}" size="60" '
                f'value="{value}">'
            )
        elif arg["type"] in ["month", "zhour", "hour", "day", "year"]:
            try:
                form = datetypes_handler(arg, int(value))
            except ValueError as exp:
                raise BadWebRequest("Invalid value provided") from exp
        elif arg["type"] == "select":
            form = make_select(
                arg["name"],
                value,
                arg["options"],
                multiple=arg.get("multiple", False),
                showvalue=arg.get("showvalue", False),
            )
        elif arg["type"] == "datetime":
            form = datetime_handler(value, arg)
        elif arg["type"] == "date":
            form = date_handler(value, arg)
        elif arg["type"] == "sday":
            form = sday_handler(value, arg)
        elif arg["type"] == "dat":
            form = dat_handler(fdict, res)
        # Handle the fun that is having it be optional
        if arg.get("optional", False):
            opton = fdict.get(f"_opt_{arg['name']}") == "on"
            # prepend
            form = (
                '<input class="optcontrol" '
                f'{"checked" if opton else ""} type="checkbox" '
                f'value="on" name="_opt_{arg["name"]}">'
                f'<div id="_opt_{arg["name"]}" style="display: '
                f'{"block" if opton else "none"};">{form}</div>'
            )
            if opton:
                add_to_plotvars(value, fdict, arg, res)
        else:
            add_to_plotvars(value, fdict, arg, res)
        formhtml += (
            f'<div class="row align-items-center apdiv">'
            f'<div class="col-sm-4">'
            f'<label class="form-label fw-semibold mb-0">'
            f"{arg['label']}</label>"
            f"</div>"
            f'<div class="col-sm-8">'
            f"{form}"
            f"</div></div>"
            "\n"
        )
    if fdict.get("_cb") == "1":
        res["pltvars"].append("_cb:1")
    res["imguri"] += "::".join(res["pltvars"]).replace("/", "-")
    if fdict.get("_wait") != "yes":
        if fmt == "text":
            try:
                resp = httpx.get(
                    f"http://iem.local{res['imguri']}.txt",
                    timeout=300,
                )
                resp.raise_for_status()
                content = resp.text
            except Exception:
                content = "Exception encountered generating text"
            res["image"] = f"<pre>\n{content}</pre>"
        elif fmt == "js":
            res["image"] = (
                '<div id="ap_container" style="width:100%s;height:400px;">'
                "</div>"
                '<div id="ap_container_controls"></div>'
            )
            res["extrascripts"] += f"""
<script src="/vendor/highcharts/{HIGHCHARTS}/highcharts.js"></script>
<script src="/vendor/highcharts/{HIGHCHARTS}/highcharts-more.js"></script>
<script src="/vendor/highcharts/{HIGHCHARTS}/modules/accessibility.js">
</script>
<script src="/vendor/highcharts/{HIGHCHARTS}/modules/exporting.js"></script>
<script src="/vendor/highcharts/{HIGHCHARTS}/modules/heatmap.js"></script>
<script src="{res["imguri"]}.js"></script>
            """
        elif fmt == "maptable":
            res["image"] = (
                '<div class="iem-maptable row" '
                f'data-geojson-src="{res["imguri"]}.geojson"></div>'
            )
            res["headextra"] += """
<link type="text/css"
 href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css"
 rel="stylesheet" />
            """
            res["extrascripts"] += """
<script
 src='https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js'>
</script>
<script src="/js/maptable.js?v=2"></script>
            """
        elif fmt in ["png", "svg"]:
            timing_secs = get_timing(apid) + 1
            res["image"] = f"""
<div class="card mb-4">
    <div class="card-header">
        <h4 class="card-title mb-0">
            <span class="badge bg-primary me-2">3</span>
            Generated Chart
        </h4>
    </div>
    <div class="card-body">
        <div id="willload" class="text-center p-4"
         data-timingsecs={timing_secs}>
            <div class="mb-3">
    <i class="bi bi-graph-up"
    style="font-size:2rem;color:#6c757d;margin-bottom:0.5rem;"
    aria-hidden="true"></i>
                <p class="mb-2">Based on recent timings, plot generation
                averages {timing_secs} seconds. Please wait while your
                chart is being generated...</p>
            </div>
            <div class="progress" style="height: 8px;">
<div id="timingbar"
    class="progress-bar progress-bar-striped progress-bar-animated bg-warning"
    role="progressbar" aria-valuenow="0"
    aria-valuemin="0" aria-valuemax="{timing_secs}"
    style="width: 0%;"></div>
            </div>
        </div>
        <div class="text-center">
            <img src="{res["imguri"]}.{fmt}" class="img-fluid"
                 id="theimage" alt="Generated chart" />
        </div>
    </div>
</div>
            """
        elif fmt == "pdf":
            res["image"] = f"""
<object id="windrose-plot" src="{res["imguri"]}.{fmt}" width="700px"
 height="700px">
    <embed src="{res["imguri"]}.{fmt}" width="700px" height="700px">
    </embed>
</object>
            """
    opts = {
        "png": "Chart Image (.PNG)",
        "svg": "Scalable Vector Graphic (.SVG)",
        "pdf": "Portable Document Format (.PDF)",
    }
    if meta.get("report"):
        opts["text"] = "Plain Text"
    if meta.get("highcharts"):
        opts["js"] = "Interactive Chart"
    if meta.get("maptable"):
        opts["maptable"] = "Interactive Map + Table"
    sel = make_select("_fmt", fmt, opts, showvalue=False)
    formhtml += (
        '<div class="row align-items-center apdiv">'
        '<div class="col-sm-4">'
        '<label class="form-label fw-semibold mb-0">'
        "Select Output Format:</label></div>"
        f'<div class="col-sm-8">{sel}</div></div>'
    )

    res["formhtml"] = f"""
<div class="row">
    <div class="col-12">
        <div class="card mb-4">
            <div class="card-header">
                <h4 class="card-title mb-0">
                    <span class="badge bg-primary me-2">2</span>
                    Configure Chart Options
                </h4>
            </div>
            <div class="card-body">
                <form method="GET" name="s" id="myForm">
                    <input type="hidden" name="_wait" value="no" id="_wait">
                    <input type="hidden" name="q" value="{apid}">
                    <div class="apopts">
                        {formhtml}
                    </div>
                    <div class="mt-4 d-flex gap-2 flex-wrap">
                        <button type="submit" class="btn btn-primary">
                                     <i class="bi bi-graph-up me-1"
                                         aria-hidden="true"></i>
                            Generate Plot
                        </button>
                        <button type="submit" name="_cb" value="1"
                                class="btn btn-outline-warning">
                                     <i class="bi bi-arrow-repeat me-1"
                                         aria-hidden="true"></i>
                            Force Update (bypass cache)
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{res["nassmsg"]}
    """
    if meta.get("report"):
        res["dataextra"] = f"""
<div class="card mb-4">
    <div class="card-header">
        <h4 class="card-title mb-0">
            <span class="badge bg-success me-2">4</span>
            Download Options
        </h4>
    </div>
    <div class="card-body">
        <div class="d-flex gap-2 flex-wrap">
            <a href="{res["imguri"]}.txt" class="btn btn-primary">
                <i class="bi bi-file-text me-1" aria-hidden="true"></i>
                Direct Text Link
            </a>
        """
    if meta.get("data"):
        res["dataextra"] += f"""
            <a href="{res["imguri"]}.csv" class="btn btn-primary">
                <i class="bi bi-download me-1" aria-hidden="true"></i>
                CSV Data
            </a>
            <a href="{res["imguri"]}.xlsx" class="btn btn-success">
                     <i class="bi bi-file-earmark-spreadsheet me-1"
                         aria-hidden="true"></i>
                     Excel Download
            </a>
        """
    if meta["maptable"]:
        res["dataextra"] += f"""
            <a href="{res["imguri"]}.geojson" class="btn btn-info">
                <i class="bi bi-map me-1" aria-hidden="true"></i>
                GeoJSON
            </a>
        """
    if meta.get("raster"):
        res["dataextra"] += f"""
            <a href="{res["imguri"]}.geotiff" class="btn btn-warning">
                <i class="bi bi-globe me-1" aria-hidden="true"></i>
                GeoTIFF
            </a>
        """

    # Close the download options card if we have any data extras
    if res["dataextra"]:
        res["dataextra"] += """
        </div>
    </div>
</div>
        """
    res["issues"] = """
<div class="alert alert-info">
    <i class="bi bi-info-circle me-2" aria-hidden="true"></i>
    If you notice plotting issues with the image above, please
    <a class="alert-link" href="/info/contacts.php">contact us</a>
    and provide the URL address currently shown by your web browser.
</div>
    """
    return res


def features_for_id(res, apid):
    """List out features for this given plotid."""
    if apid < 1:
        return ""
    s = """
<h3>IEM Daily Features using this plot</h3>
<p>The IEM Daily Features found on this website often utilize plots found
on this application.  Here is a listing of features referencing this
plot type.</p>
<ul>
    """
    with get_sqlalchemy_conn("mesosite") as conn:
        extra = ""
        params = {"appurl": f"q={apid}(&|$)"}
        if res["frontend"]:
            extra = " or strpos(appurl, :fe) = 1"
            params["fe"] = res["frontend"]
        # careful here as we use US Central Time for dates
        df = pd.read_sql(
            sql_helper(
                "select date(valid at time zone 'America/Chicago') as dt, "
                "title from feature "
                "WHERE (substr(appurl, 1, 14) = '/plotting/auto' and "
                " appurl ~* :appurl) {extra} and valid < now() "
                "ORDER by valid DESC",
                extra=extra,
            ),
            conn,
            params=params,
            parse_dates="dt",
            index_col="dt",
        )
    for dt, row in df.iterrows():
        s += (
            f'<li><strong><a href="/onsite/features/cat.php?'
            f'day={dt:%Y-%m-%d}">'
            f"{dt:%d %b %Y}</a></strong>: {row['title']}</li>\n"
        )
    s += "</ul>"
    return s


def generate_autoplot_list(apid):
    """The select list of available autoplots."""
    s = (
        '<select name="q" class="iemselect2 form-control-lg" '
        'data-width="100%">'
        "\n"
    )
    for entry in autoplot_data["plots"]:
        s += f'<optgroup label="{entry["label"]}">\n'
        for opt in entry["options"]:
            selected = ' selected="selected"' if opt["id"] == apid else ""
            s += (
                f'<option value="{opt["id"]}"{selected}>{opt["label"]} '
                f"(#{opt['id']})</option>\n"
            )
        s += "</optgroup>\n"

    s += "</select>\n"
    return s


def generate_trending():
    """Build the trending list."""
    res = "<h3>Trending Autoplots over Past 6 Hours</h3>"
    res += '<table class="table table-striped table-bordered">\n'
    res += "<tr><th>Plot</th><th>Requests</th></tr>\n"
    try:
        # This is external API, so no need for internal routing
        data = httpx.get(
            (
                "http://mesonet.agron.iastate.edu"
                "/api/1/iem/trending_autoplots.json"
            ),
            timeout=5,
        ).json()
        for entry in data["data"][:5]:
            label = "Unknown"
            for ap in autoplot_data["plots"]:
                if label != "Unknown":
                    break
                for opt in ap["options"]:
                    if opt["id"] == entry["appid"]:
                        label = opt["label"]
                        break
            res += (
                f'<tr><td><a href="/plotting/auto/?q={entry["appid"]}">'
                f"#{entry['appid']}. {label}</a></td><td>{entry['count']:,}"
                "</td></tr>\n"
            )
    except Exception as exp:
        LOG.exception(exp)
        res += '<tr><th colspan="2">Failed to Load</th></tr>'
    res += "</table>"
    return res


def generate_overview(apid):
    """If we don't have an apid set (==0), then fill in the overview."""
    if apid > 0:
        return ""
    fn = "/mesonet/share/pickup/autoplot/overview.html"
    if not os.path.isfile(fn):
        LOG.warning(f"{fn} is missing")
        return ""
    with open(fn, encoding="utf8") as fh:
        content = fh.read()
    return f"""
<div class="row">
    <div class="col-md-6">
<h1>Visual Overview of All Autoplots</h1>
<p>Below you will find an example resulting image from each of the autoplots
available.  Click on the image or title to navigate to that autoplot. These are
grouped into sections as they also appear grouped in the dropdown selection
box above.</p>
    </div>
    <div class="col-md-6">
    {generate_trending()}
    </div>
</div>


    {content}
    """


def generate(fdict, headers, cookies):
    """Return a dict of things for the template engine."""
    try:
        apid = int(fdict.get("q", 0))
    except ValueError:
        apid = 0
    if apid < 0 or apid > 1_000:  # arb
        raise BadWebRequest("Invalid plot id")
    res = generate_form(apid, fdict, headers, cookies)
    content = f"""
<div class="row">
    <div class="col-12">
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h3 class="card-title mb-0">
                    <i class="bi bi-graph-up me-2" aria-hidden="true"></i>
                    Automated Data Plotter
                </h3>
            </div>
            <div class="card-body">
                <p class="lead">This application dynamically generates many
                types of graphs derived from various IEM data sources.
                Feel free to use these generated graphics in whatever way
                you wish.</p>
                <div class="d-flex gap-2 flex-wrap">
                    <a href="/plotting/auto/"
                       class="btn btn-outline-secondary btn-sm">
                                <i class="bi bi-arrow-repeat me-1"
                                    aria-hidden="true"></i>
                        Reset App
                    </a>
                    <a href="/explorer/"
                       class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-map me-1" aria-hidden="true"></i>
                        IEM Explorer (Simplified)
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card mb-4">
            <div class="card-header">
                <h4 class="card-title mb-0">
                    <span class="badge bg-primary me-2">1</span>
                    Select a Chart Type
                </h4>
            </div>
            <div class="card-body">
                <form method="GET" name="t">
                    <div class="row g-3 align-items-end">
                        <div class="col-12 col-lg-8">
                            <label for="chart-select" class="form-label">
                                Choose from available chart types:
                            </label>
                            {generate_autoplot_list(apid)}
                        </div>
                        <div class="col-12 col-lg-4">
                            <button type="submit"
                                    class="btn btn-primary w-100">
                                          <i class="bi bi-arrow-right me-1"
                                              aria-hidden="true"></i>
                                Select Plot Type
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

{res["formhtml"]}

{res["description"]}

<div class="row">
    <div class="col-12">
        {res["image"]}

        {res["dataextra"]}

        {res["issues"]}
    </div>
</div>

{features_for_id(res, apid)}

{generate_overview(apid)}

    """
    return {
        "title": res["title"],
        "content": content,
        "jsextra": f"""
<script src="/vendor/openlayers/{OPENLAYERS}/ol.js" type="text/javascript">
</script>
<script src='/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.js'></script>
{res["extrascripts"]}
<script src="js/mapselect.js?v=2"></script>
<script src="/js/select2.js?v=3"></script>
<script type="module" src="/plotting/auto/index.module.js"></script>
        """,
        "headextra": f"""
 <link rel="stylesheet" type="text/css"
 href="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css" />
<link
 href="https://cdn.jsdelivr.net/npm/tom-select@2.4.3/dist/css/tom-select.css"
 rel="stylesheet">
<link
 href="https://cdn.jsdelivr.net/npm/tom-select@2.4.3/dist/css/tom-select.bootstrap5.css"
 rel="stylesheet">

<link rel="stylesheet"
 href="/vendor/openlayers/{OPENLAYERS}/ol.css" type="text/css">
<link type="text/css"
 href="/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.css"
 rel="stylesheet" />
<link type="text/css" href="/plotting/auto/index.css" rel="stylesheet" />
 {res["headextra"]}
        """,
    }


def remove_all_cookies(headers, cookiestr):
    """Unset things that should have not gotten set."""
    for token in cookiestr.split(";"):
        meat = token if token.find("=") == -1 else token[: token.find("=")]
        headers.append(
            (
                "Set-Cookie",
                f"={meat.strip()}; Path=/plotting/auto/; Max-Age=-1",
            )
        )


@iemapp(parse_times=False, allowed_as_list=["ltype"])
def application(environ: dict, start_response: callable) -> list[bytes]:
    """mod-wsgi handler."""
    cookies = get_cookie_dict(environ)
    headers = [("Content-type", "text/html")]
    # invalid cookies may invalidate the entire cookie parsing
    # https://bugs.python.org/issue41945
    if not cookies and environ.get("HTTP_COOKIE", "") != "":
        remove_all_cookies(headers, environ["HTTP_COOKIE"])
    tdict = generate(environ, headers, cookies)
    start_response("200 OK", headers)
    return [TEMPLATE.render(tdict).encode("utf-8")]
