"""IEM Autoplot Frontend.

IEM_APPID 92
"""

import calendar
import os
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

HIGHCHARTS = "11.3.0"
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
<div class="popup" id="popup_{network}_{name}"></div>
"""


def networkselect_handler(value, arg, res):
    """Select a station from a given network."""
    if not isinstance(arg["network"], list):
        res["pltvars"].append(f"network:{arg['network']}")
    return station_select(
        arg["network"],
        value,
        arg["name"],
        select_all=arg.get("all", False),
    ) + map_select_widget(arg["network"], arg["name"])


def station_handler(value, arg, fdict, res, typ):
    """Generate HTML."""
    networks = {}
    pgconn, cursor = get_dbconnc("mesosite")
    netlim = ""
    if typ == "zstation":
        netlim = "WHERE id ~* 'ASOS'"
    elif typ == "station":
        netlim = "WHERE id ~* 'CLIMATE'"
    elif typ == "sid" and not arg.get("include_climodat", False):
        netlim = "WHERE id !~* 'CLIMATE'"
    cursor.execute(f"SELECT id, name from networks {netlim} ORDER by name ASC")
    for row in cursor:
        networks[row["id"]] = row["name"]
    pgconn.close()
    # We could have two plus zstations
    networkcgi = "network"
    if arg["name"][-1].isdigit():
        networkcgi += arg["name"][-1]
    network = arg.get("network", "IA_ASOS")
    network = html_escape(fdict.get(networkcgi, network))
    netselect = make_select(
        networkcgi, network, networks, jscallback="onNetworkChange"
    )
    select = station_select(network, value, arg["name"])
    res["pltvars"].append(f"{networkcgi}:{network}")
    return netselect + " " + select + map_select_widget(network, arg["name"])


def ugc_select(state, ugc):
    """Generate a select for a given state."""
    pgconn, cursor = get_dbconnc("postgis")
    cursor.execute(
        "SELECT ugc, name from ugcs WHERE substr(ugc, 1, 2) = %s and "
        "end_ts is null ORDER by name ASC",
        (state,),
    )
    ar = {}
    for row in cursor:
        ar[row["ugc"]] = (
            f"{row['name']} {'(Zone)' if row['ugc'][2] == 'Z' else ''}"
        )
    pgconn.close()
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
        cssclass="cmapselect",
        showvalue=False,
    )
    checked = ' checked="checked"' if reverse_on else ""
    s += (
        f'&nbsp; <input type="checkbox" name="{arg["name"]}_r" '
        f'value="on"{checked}> Reverse Colormap?'
    )
    res["pltvars"].append(f"{arg['name']}:{value}{'_r' if reverse_on else ''}")
    res["jsextra"] += """
function formatState (state) {
    if (!state.id) {
        return state.text;
    }
    var baseUrl = "/pickup/cmaps";
    var $state = $(
        '<span><img src="' + baseUrl + '/' + state.element.value +
        '.png" /> ' + state.text + '</span>'
    );
    return $state;
};

$(".cmapselect").select2({
    templateSelection: formatState,
    templateResult: formatState
});
    """
    return s


def datetypes_handler(arg, value):
    """Handle simple forms."""
    try:
        value = int(value)
    except ValueError as exp:
        LOG.info(exp)
    if arg["type"] == "month":
        items = zip(range(1, 13), calendar.month_name[1:])
    elif arg["type"] in ["zhour", "hour"]:
        fmt = "%I %p" if arg["type"] == "hour" else "%H Z"
        items = zip(
            range(24),
            [utc(2000, 1, 1, hr).strftime(fmt) for hr in range(24)],
        )
    elif arg["type"] == "day":
        items = zip(range(1, 32), range(1, 32))
    else:
        vmin = arg.get("min", 1893)
        vmax = arg.get("max", utc().year)
        items = zip(range(vmin, vmax + 1), range(vmin, vmax + 1))
    return make_select(arg["name"], value, dict(items), showvalue=False)


def sday_handler(value, arg, res):
    """Handler for datetime instances."""
    dpname = f"datepicker_{arg['name']}"
    vmin = arg.get("min", "0101")
    vmax = arg.get("max", "1231")
    # account for legacy URLs that had dates here
    if value.find("/") > -1:
        value = f"{value[5:7]}{value[8:10]}"

    def _todate(val):
        """convert to a timestamp value."""
        return f"2000/{val[:2]}/{val[2:]}"

    res["jsextra"] += f"""
$( '#{dpname}' ).datepicker({{
    beforeShow: function (input, inst) {{
        inst.dpDiv.addClass('sday');
    }},
    onClose: function(dateText, inst) {{
        inst.dpDiv.removeClass('sday');
    }},
    changeMonth: true,
    changeYear: false,
    dateFormat: "mm/dd",
    altFormat: "mmdd",
    altField: "#alt_{dpname}",
    endDate: new Date('{_todate(vmax)}'),
    startDate: new Date('{_todate(vmin)}')
}});
$("#{dpname}").datepicker(
    'setDate', new Date('{_todate(value)}')
);
    """
    return (
        f'<input type="text" id="{dpname}"> (mm/dd)'
        f'<input type="hidden" name="{arg["name"]}" value="{value}" '
        f'id="alt_{dpname}">'
    )


def date_handler(value, arg, res):
    """Handler for datetime instances."""
    dpname = f"datepicker_{arg['name']}"
    vmin = arg.get("min", "1893/1/1")
    vmax = arg.get("max", utc().strftime("%Y/%m/%d"))
    res["jsextra"] += f"""
$( '#{dpname}' ).datepicker({{
    changeMonth: true,
    changeYear: true,
    dateFormat: "yy/mm/dd",
    endDate: new Date('{vmax}'),
    startDate: new Date('{vmin}')
}});
$("#{dpname}").datepicker(
    'setDate', new Date('{value}')
);
    """
    return (
        f'<input type="text" name="{arg["name"]}" id="{dpname}" > (YYYY/mm/dd)'
    )


def datetime_handler(value, arg, res):
    """Handler for datetime instances."""
    dpname = f"fp_{arg['name']}"
    vmax = arg.get("max", utc().strftime("%Y/%m/%d %H%M"))
    res["jsextra"] += f"""
$( "#{dpname}" ).flatpickr({{
    enableTime: true,
    dateFormat: "Y/m/d Hi",
    time_24hr: true,
    allowInput: true,
    defaultDate: moment('{value}', 'YYYY/MM/DD HHmm').toDate(),
    maxDate: moment('{vmax}', 'YYYY/MM/DD HHmm').toDate(),
    minDate: moment('{arg["min"]}', 'YYYY/MM/DD HHmm').toDate()}});
    """
    return (
        f'<input type="text" name="{arg["name"]}" id="{dpname}" '
        "> (YYYY/mm/dd HH24MI)"
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
    if isinstance(value, (str, int, float)):
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
    res["jsextra"] += f"""
$("#dat").datepicker({{
    changeMonth: true,
    changeYear: true,
    dateFormat: "yy/mm/dd",
    startDate: new Date('2001/01/01'),
    endDate: new Date('{utc():%Y/%m/%d}'),
    onSelect: function(dateText) {{
        onNetworkChange(dateText);
    }}
}});
$("#dat").datepicker(
    'setDate', new Date('{dt}')
);
    """
    return f'<input type="text" name="dat" id="dat"> (YYYY/mm/dd) &nbsp; {ss}'


def generate_form(apid, fdict, headers, cookies):
    """Generate out the form, oh boy!"""
    res = {
        "nassmsg": "",
        "description": "",
        "imguri": f"/plotting/auto/plot/{apid}/",
        "pltvars": [],
        "jsextra": "",
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
    try:
        resp = httpx.get(
            f"http://iem.local/plotting/auto/meta/{apid}.json",
            timeout=60,
        )
        resp.raise_for_status()
    except Exception as exp:
        LOG.exception(exp)
        return res
    meta = resp.json()
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
            form = make_select(arg["name"], value, state_names)
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
            form = datetime_handler(value, arg, res)
        elif arg["type"] == "date":
            form = date_handler(value, arg, res)
        elif arg["type"] == "sday":
            form = sday_handler(value, arg, res)
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
            f'<div class="row apdiv"><div class="col-md-3">{arg["label"]}'
            f'</div><div class="col-md-9">{form}</div></div>'
            "\n"
        )
    if fdict.get("_cb") == "1":
        res["pltvars"].append("_cb:1")
    res["imguri"] += "::".join(res["pltvars"]).replace("/", "-")
    if fdict.get("_wait") != "yes":
        if fmt == "text":
            content = httpx.get(
                f"http://iem.local{res['imguri']}.txt",
                timeout=300,
            ).text
            res["image"] = f"<pre>\n{content}</pre>"
        elif fmt == "js":
            res["image"] = (
                '<div id="ap_container" style="width:100%s;height:400px;">'
                "</div>"
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
 href="/vendor/jquery-datatables/1.10.24/datatables.min.css"
 rel="stylesheet" />
            """
            res["extrascripts"] += """
<script src='/vendor/jquery-datatables/1.10.24/datatables.min.js'></script>
<script src="/js/maptable.js"></script>
<script>
var maptable;
$(document).ready(function(){{
    maptable = $("div.iem-maptable").MapTable();
}});
</script>
            """
        elif fmt in ["png", "svg"]:
            timing_secs = get_timing(apid) + 1
            res["image"] = f"""
<div id="willload" style="height: 200px;">
        <p><span class="fa fa-arrow-down"></span>
        Based on a sampling of recent timings for this application, plot
        generation
 time has averaged {timing_secs} seconds. Hold on for the plot is generating
 now!</p>
        <div class="progress progress-striped active">
                <div id="timingbar" class="progress-bar progress-bar-warning"
                role="progressbar"
             aria-valuenow="0" aria-valuemin="0" aria-valuemax="{timing_secs}"
                 style="width: 0%;"></div>
        </div>
</div>
<br clear="all" />
        <img src="{res["imguri"]}.{fmt}" class="img img-responsive"
         id="theimage" />
            """
            res["jsextra"] += f"""
var timing = 0;
var progressBar = setInterval(function (){{
        if (timing >= {timing_secs} ||
            $('#willload').css('display') == 'none'){{
                clearInterval(progressBar);
        }}
        var width = (timing / {timing_secs}) * 100.;
        $("#timingbar").css('width', width +'%').attr('aria-valuenow', width);
        timing = timing + 0.2;
}}, 200);
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
        '<div class="row apdiv"><div class="col-md-3">Select Output Format:'
        f'</div><div class="col-md-9">{sel}</div></div>'
    )

    res["formhtml"] = f"""
<style>
.apopts .row:nth-of-type(odd) {{
  background-color: #EEEEEE;
}}
.apopts .row:nth-of-type(even) {{
  background-color: #FFFFFF;
}}
.apdiv {{
    margin-top: 3px;
    margin-bottom: 3px;
}}
.optcontrol {{
  float: left;
  margin-right: 10px !important;
}}
.ui-datepicker-year {{
  color: #000;
}}
.sday .ui-datepicker-year {{
  display: none;
}}
.ui-datepicker-month {{
  color: #000;
}}
.popup {{
    background-color: rgba(0, 0, 0, 0.75);
    color: #FFF;
    font-weight: bold;
    font-size: 1.2em;
    padding-left: 20px;
    padding-right: 20px;
    z-index: 10002;
}}
.highcharts-root {{
  font-size: 16px !important;
}}
</style>
<script>
function onNetworkChange(newnetwork){{
    $("#_wait").val("yes");
    $('form#myForm').submit();
}}
</script>
        <h4><span class="fa fa-arrow-right"></span>
        Second, select specific chart options::</h4>
        <form method="GET" name="s" id="myForm">
        <input type="hidden" name="_wait" value="no" id="_wait">
        <input type="hidden" name="q" value="{apid}">
        <div class="container-fluid apopts">
        {formhtml}
        </div>
        <button type="submit">Make Plot with Options</button>
        <button type="submit" name="_cb" value="1">
        Force Updated Plot (no caching)</button>
</form>
    {res["nassmsg"]}
    """
    if meta.get("report"):
        res["dataextra"] = f"""
<a href="{res["imguri"]}.txt" class="btn btn-primary">
<i class="fa fa-table"></i> Direct/Stable Link to Text</a> &nbsp;
        """
    if meta.get("data"):
        res["dataextra"] += f"""
<a href="{res["imguri"]}.csv" class="btn btn-primary">
<i class="fa fa-table"></i> View Data (as csv)</a> &nbsp;
<a href="{res["imguri"]}.xlsx" class="btn btn-primary">
<i class="fa fa-table"></i> Download as Excel</a> &nbsp;
        """
    if meta["maptable"]:
        res["dataextra"] += f"""
<a href="{res["imguri"]}.geojson" class="btn btn-primary">
<i class="fa fa-map"></i> Download as GeoJSON</a> &nbsp;
        """
    if meta.get("raster"):
        res["dataextra"] += f"""
<a href="{res["imguri"]}.geotiff" class="btn btn-primary">
<i class="fa fa-map"></i> Download as GeoTIFF</a> &nbsp;
        """
    res["issues"] = """
    <div><span class="fa fa-info"></span>
    If you notice plotting issues with the image above, please
    do <a class="alert-link" href="/info/contacts.php">let us know</a>
    by providing the
    URL address currently shown by your web browser.</div>
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
    s = '<select name="q" class="iemselect2" data-width="100%">\n'
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
        data = httpx.get(
            "http://iem.local/api/1/iem/trending_autoplots.json", timeout=5
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
    res = generate_form(apid, fdict, headers, cookies)
    content = f"""
<h3>Automated Data Plotter</h3>

<p>This application dynamically generates many types of graphs.  These graphs
are derived from processing of various data sources done by the IEM.  Please
feel free to use these generated graphics in whatever way you wish.
<a href="/plotting/auto/">Reset App</a>. The
<a href="/explorer/">IEM Explorer</a> application offers a simplified frontend
to some of these autoplots.</p>

<br /><form method="GET" name="t">
<div class="form-group">
<h4><span class="fa fa-arrow-right"></span> First, select a chart type::</h4>
{generate_autoplot_list(apid)}
<input type="submit" value="Select Plot Type" />
</div>
</form>

<hr />

{res["formhtml"]}

{res["description"]}

<hr>

{res["image"]}

{res["dataextra"]}

{res["issues"]}

{features_for_id(res, apid)}

{generate_overview(apid)}

    """
    return {
        "title": "Automated Data Plotter",
        "content": content,
        "jsextra": f"""
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src="/vendor/flatpickr/4.6.9/flatpickr.min.js"></script>
<script src="/vendor/select2/4.1.0rc0/select2.min.js"></script>
<script src="/vendor/openlayers/{OPENLAYERS}/ol.js" type="text/javascript">
</script>
<script src='/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.js'></script>
{res["extrascripts"]}
<script src="js/mapselect.js?v=2"></script>
<script>
function hideImageLoad(){{
        // console.log("load() fired...");
        $('#willload').css('display', 'none');
}}
$(document).ready(function(){{
    {res["jsextra"]}
    $('.optcontrol').change(function(){{
        if (this.checked){{
                $("#"+ this.name).css('display', 'block');
        }} else {{
                $("#"+ this.name).css('display', 'none');
        }}
    }});
        $('#theimage').on('load', function(){{
                hideImageLoad();
        }});
        $('#theimage').on('error', function(){{
                hideImageLoad();
        }});
    // The image may be cached and return to the user before this javascript
    // is hit, so we do a check to see if it is indeed loaded now
        if ($("#theimage").get(0) && $("#theimage").get(0).complete){{
                hideImageLoad();
        }}
    $(".iemselect2").select2();
}});
</script>
        """,
        "headextra": f"""
 <link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.css" />
 <link rel="stylesheet" type="text/css"
 href="/vendor/flatpickr/4.6.9/flatpickr.min.css"/>
 <link rel="stylesheet" type="text/css"
 href="/vendor/select2/4.1.0rc0/select2.min.css"/ >
<link rel="stylesheet"
 href="/vendor/openlayers/{OPENLAYERS}/ol.css" type="text/css">
<link type="text/css"
 href="/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.css"
 rel="stylesheet" />
<style>
    .select2-results .select2-disabled,
    .select2-results__option[aria-disabled=true] {{
    display: none;
    }}
.ui-datepicker{{
    width: 17em; padding: .2em .2em 0; z-index: 9999 !important; }}
.cmapselect{{
    width: 400px; }}
</style>
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
def application(environ, start_response):
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
