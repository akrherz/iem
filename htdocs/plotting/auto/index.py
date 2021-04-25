"""IEM Autoplot Frontend.

IEM_APPID 92
"""
# stdlib
from datetime import datetime, date
import calendar
import os
import sys
from html import escape

# Third Party
import requests
from paste.request import get_cookie_dict, parse_formvars
from pyiem.htmlgen import make_select, station_select
from pyiem.util import get_dbconn, utc
from pyiem.templates.iem import TEMPLATE
from pyiem.reference import state_names, SECTORS
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE

BASEDIR, WSGI_FILENAME = os.path.split(__file__)
if BASEDIR not in sys.path:
    sys.path.insert(0, BASEDIR)
# Local
import scripts  # noqa

HIGHCHARTS = "8.2.2"
OPENLAYERS = "6.4.3"
CSECTORS = state_names
CSECTORS.update({"conus": "CONUS"})
CSECTORS.update(SECTORS)
CMAPS = {
    "Perceptually Uniform Sequential": [
        "viridis",
        "plasma",
        "inferno",
        "magma",
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
        "hsv",
        "gist_rainbow",
        "rainbow",
        "jet",
        "nipy_spectral",
        "gist_ncar",
    ],
}


def networkselect_handler(value, arg, res):
    """Select a station from a given network."""
    res["pltvars"].append(f"network:{arg['network']}")
    return station_select(
        arg["network"],
        value,
        arg["name"],
        select_all=arg.get("all", False),
    )


def station_handler(value, arg, fdict, res, typ):
    """Generate HTML."""
    networks = {}
    cursor = get_dbconn("mesosite").cursor()
    netlim = ""
    if typ == "zstation":
        netlim = "WHERE id ~* 'ASOS' or id = 'AWOS'"
    elif typ == "station":
        netlim = "WHERE id ~* 'CLIMATE'"
    cursor.execute(f"SELECT id, name from networks {netlim} ORDER by name ASC")
    for row in cursor:
        networks[row[0]] = row[1]
    # We could have two plus zstations
    networkcgi = "network"
    if arg["name"][-1].isdigit():
        networkcgi += arg["name"][-1]
    network = arg.get("network", "IA_ASOS")
    network = fdict.get(networkcgi, network)
    netselect = make_select(
        networkcgi, network, networks, jscallback="onNetworkChange"
    )
    select = station_select(network, value, arg["name"])
    res["pltvars"].append(f"{networkcgi}:{network}")
    return netselect + " " + select


def ugc_select(state, ugc):
    """Generate a select for a given state."""
    cursor = get_dbconn("postgis").cursor()
    cursor.execute(
        "SELECT ugc, name from ugcs WHERE substr(ugc, 1, 2) = %s and "
        "end_ts is null ORDER by name ASC",
        (state,),
    )
    ar = {}
    for row in cursor:
        ar[row[0]] = f"{row[1]} {'(Zone)' if row[0][2] == 'Z' else ''}"
    return make_select("ugc", ugc, ar)


def ugc_handler(value, state, res):
    """Handle selection of UGCs."""
    if state is None:
        state = "IA"
    state_select = make_select(
        "state", state, state_names, jscallback="onNetworkChange"
    )
    res["pltvars"].append(f"state:{state}")
    return state_select + " " + ugc_select(state, value)


def vtec_ps_handler(fdict, arg):
    """Handle VTEC Phenomena + Significance."""
    suffix = arg["name"]
    default_p, default_s = arg["default"].split(".")
    value = escape(fdict.get(f"phenomena{suffix}", default_p))
    s = make_select(f"phenomena{suffix}", value, VTEC_PHENOMENA)
    value = escape(fdict.get(f"significance{suffix}", default_s))
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
    )
    checked = ' checked="checked"' if reverse_on else ""
    s += (
        f"&nbsp; <input type=\"checkbox\" name=\"{arg['name']}_r\" "
        f'value="on"{checked}> Reverse Colormap?'
    )
    res["pltvars"].append(f"{arg['name']}:{value}{'_r' if reverse_on else ''}")
    res[
        "jsextra"
    ] += """
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
    return make_select(arg["name"], value, dict(items))


def date_handler(value, arg, res):
    """Handler for datetime instances."""
    dpname = f"datepicker_{arg['name']}"
    vmin = arg.get("min", "1893/1/1")
    vmax = arg.get("max", utc().strftime("%Y/%m/%d"))
    res[
        "jsextra"
    ] += f"""
$( '#{dpname}' ).datepicker({{
    changeMonth: true,
    changeYear: true,
    dateFormat: "yy/mm/dd",
    maxDate: new Date('{vmax}'),
    minDate: new Date('{vmin}')
}});
$("#{dpname}").datepicker(
    'setDate', new Date('{value}')
);
    """
    return (
        f"<input type=\"text\" name=\"{arg['name']}\" id=\"{dpname}\" "
        "> (YYYY/mm/dd)"
    )


def datetime_handler(value, arg, res):
    """Handler for datetime instances."""
    dpname = f"timepicker_{arg['name']}"
    vmax = arg.get("max", utc().strftime("%Y/%m/%d %H%M"))
    res[
        "jsextra"
    ] += f"""
$( "#{dpname}" ).datetimepicker({{
    controlType: 'select',
    changeMonth: true,
    changeYear: true,
    dateFormat: "yy/mm/dd",
    timeFormat: "HHmm",
    maxDateTime: $.datepicker.parseDateTime(
        'yy/mm/dd', 'HHmm', '{vmax}'),
    minDateTime: $.datepicker.parseDateTime(
        'yy/mm/dd', 'HHmm', '{arg['min']}')}});
$("#{dpname}").datetimepicker('setDate',
    $.datepicker.parseDateTime(
        'yy/mm/dd', 'HHmm', '{value}'));
    """
    return (
        f"<input type=\"text\" name=\"{arg['name']}\" id=\"{dpname}\" "
        "> (YYYY/mm/dd HH24MI)"
    )


def add_to_plotvars(value, fdict, arg, res):
    """Add to our plotvars."""
    if arg["type"] == "vtec_ps":
        suffix = arg["name"]
        value = fdict.get(f"phenomena{suffix}", "SV")
        res["pltvars"].append(f"phenomena{suffix}:{value}")
        value = fdict.get(f"significance{suffix}", "W")
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


def set_cookie(cookies, headers, name, value):
    """Optionally set a cookie in the response headers."""
    if value == cookies.get(name):
        return
    headers.append(
        (
            "Set-Cookie",
            f"{name}:{value}; Path=/plotting/auto/; Max-Age=8640000",
        )
    )


def get_cookie_value(arg, cookies):
    """Some custom cruft here."""
    if arg["type"] in ["state", "csector"]:
        return cookies.get(arg["name"])
    if arg["type"] == "networkselect":
        return cookies.get(f"{arg['name']}_{arg['network']}")


def get_timing(apid):
    """Get a timing sample."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT avg(timing)::int from autoplot_timing where appid = %s "
        "and valid > (now() - '7 days'::interval)",
        (apid,),
    )
    timing = cursor.fetchone()[0]
    return timing if timing is not None else -1


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
    }
    if apid == 0:
        return res
    fmt = fdict.get("_fmt")
    # This should be instant, but the other end may be doing a thread
    # restart, which takes a bit of time.
    req = requests.get(
        f"http://iem.local/plotting/auto/meta/{apid}.json",
        timeout=60,
    )
    if req.status_code != 200:
        return res
    meta = req.json()
    if meta.get("description"):
        res["description"] = (
            '<div class="alert alert-info"><h4>Plot Description:</h4>'
            f"{meta['description']}</div>"
        )
    if fmt is None:
        if meta.get("report") is not None:
            fmt = "text"
        elif meta.get("highcharts") is not None:
            fmt = "js"
        elif meta.get("maptable") is not None:
            fmt = "maptable"
        fmt = "png"
    if meta.get("nass") is not None:
        res[
            "nassmsg"
        ] = """
<div class="alert alert-warning">This data presentation utilizes the
        <a href="http://quickstats.nass.usda.gov/">USDA NASS Quickstats</a>.
        This presentation is not endorsed nor certified by USDA.
</div>
        """
    form = ""
    formhtml = ""
    for arg in meta["arguments"]:
        value = fdict.get(arg["name"], get_cookie_value(arg, cookies))
        if value is None:
            value = arg["default"]
        if arg["type"] in ["zstation", "sid", "station"]:
            form = station_handler(value, arg, fdict, res, arg["type"])
        elif arg["type"] == "ugc":
            form = ugc_handler(value, fdict.get("state"), res)
        elif arg["type"] == "networkselect":
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
        elif arg["type"] in ["text", "int", "float"]:
            form = (
                f"<input type=\"text\" name=\"{arg['name']}\" size=\"60\" "
                f'value="{value}">'
            )
        elif arg["type"] in ["month", "zhour", "hour", "day", "year"]:
            form = datetypes_handler(arg, value)
        elif arg["type"] == "select":
            form = make_select(
                arg["name"],
                value,
                arg["options"],
                multiple=arg.get("multiple", False),
                showvalue=False,
            )
        elif arg["type"] == "datetime":
            form = datetime_handler(value, arg, res)
        elif arg["type"] == "date":
            form = date_handler(value, arg, res)
        # Handle the fun that is having it be optional
        if arg.get("optional", False):
            opton = fdict.get(f"_opt_{arg['name']}") == "on"
            # prepend
            form = (
                '<input class="optcontrol" %s type="checkbox" '
                'value="on" name="%s"><div id="%s" '
                'style="display: %s;">%s</div>'
            ) % (
                'checked="checked"' if opton else "",
                "_opt_" + arg["name"],
                "_opt_" + arg["name"],
                "block" if opton else "none",
                form,
            )
            if opton:
                add_to_plotvars(value, fdict, arg, res)
        else:
            add_to_plotvars(value, fdict, arg, res)
        formhtml += f"<tr><td>{arg['label']}</td><td>{form}</td></tr>\n"
    if fdict.get("_cb") == "1":
        res["pltvars"].append("_cb:1")
    res["imguri"] += "::".join(res["pltvars"]).replace("/", "-")
    if fdict.get("_wait") != "yes":
        if fmt == "text":
            content = requests.get(
                f"http://iem.local{res['imguri']}.txt",
                timeout=300,
            ).content
            res["image"] = f"<pre>\n{content}</pre>"
        elif fmt == "js":
            res["image"] = (
                '<div id="ap_container" style="width:100%s;height:400px;">'
                "</div>"
            )
            res[
                "extrascripts"
            ] += f"""
<script src="/vendor/highcharts/{HIGHCHARTS}/highcharts.js"></script>
<script src="/vendor/highcharts/{HIGHCHARTS}/highcharts-more.js"></script>
<script src="/vendor/highcharts/{HIGHCHARTS}/modules/exporting.js"></script>
<script src="{res['imguri']}.js"></script>
            """
        elif fmt == "maptable":
            res["image"] = (
                '<div class="iem-maptable row" '
                f'data-geojson-src="{res["imguri"]}.geojson"></div>'
            )
            res[
                "headextra"
            ] += f"""
<link rel="stylesheet"
 href="/vendor/openlayers/{OPENLAYERS}/ol.css" type="text/css">
<link type="text/css"
 href="/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.css"
 rel="stylesheet" />
<link type="text/css"
 href="/vendor/jquery-datatables/1.10.24/datatables.min.css"
 rel="stylesheet" />
            """
            res[
                "extrascripts"
            ] += f"""
<script src="/vendor/openlayers/{OPENLAYERS}/ol.js" type="text/javascript">
</script>
<script src='/vendor/openlayers/{OPENLAYERS}/ol-layerswitcher.js'></script>
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
            res[
                "image"
            ] = f"""
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
        <img src="{res['imguri']}.{fmt}" class="img img-responsive"
         id="theimage" />
            """
            res[
                "jsextra"
            ] += f"""
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
            res[
                "image"
            ] = f"""
<object id="windrose-plot" src="{res['imguri']}.{fmt}" width="700px"
 height="700px">
    <embed src="{res['imguri']}.{fmt}" width="700px" height="700px">
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
    sel = make_select("_fmt", fmt, opts)
    formhtml += f"<tr><td>Select Output Format:</td><td>{sel}</td></tr>"
    res[
        "formhtml"
    ] = f"""
<style>
.optcontrol {{
  float: left;
  margin-right: 10px !important;
}}
.ui-datepicker-year {{
  color: #000;
}}
.ui-datepicker-month {{
  color: #000;
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
        <table class="table table-striped">
                <thead><tr><th>Description</th><th>Value</th></tr></thead>
        {formhtml}
        </table>
        <button type="submit">Make Plot with Options</button>
        <button type="submit" name="_cb" value="1">
        Force Updated Plot (no caching)</button>
</form>
    """
    if meta.get("data"):
        res[
            "dataextra"
        ] += f"""
<a href="{res['imguri']}.csv" class="btn btn-primary">
<i class="fa fa-table"></i> View Data (as csv)</a> &nbsp;
<a href="{res['imguri']}.xlsx" class="btn btn-primary">
<i class="fa fa-table"></i> Download as Excel</a> &nbsp;
        """
        if meta["maptable"]:
            res[
                "dataextra"
            ] += f"""
<a href="{res['imguri']}.geojson" class="btn btn-primary">
<i class="fa fa-map"></i> Download as GeoJSON</a> &nbsp;
            """
    res[
        "issues"
    ] = """
    <div><span class="fa fa-info"></span>
    If you notice plotting issues with the image above, please
    do <a class="alert-link" href="/info/contacts.php">let us know</a>
    by providing the
    URL address currently shown by your web browser.</div>
    """
    return res


def features_for_id(apid):
    """List out features for this given plotid."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    s = """
<h3>IEM Daily Features using this plot</h3>
<p>The IEM Daily Features found on this website often utilize plots found
on this application.  Here is a listing of features referencing this
plot type.</p>
<ul>
    """
    cursor.execute(
        "select to_char(valid, 'dd Mon YYYY'), "
        "to_char(valid, 'YYYY/mm/dd'), title from feature "
        "WHERE substr(appurl, 1, 14) = '/plotting/auto' and "
        " appurl ~* %s ORDER by valid DESC",
        (f"q={apid}(&|$)",),
    )
    for row in cursor:
        s += (
            f'<li><strong><a href="/onsite/features/cat.php?day={row[1]}">'
            f"{row[0]}</a></strong>: {row[2]}</li>\n"
        )
    s += "</ul>"
    return s


def generate_autoplot_list(apid):
    """The select list of available autoplots."""
    s = '<select name="q" class="iemselect2">\n'
    for entry in scripts.data["plots"]:
        s += f"<optgroup label=\"{entry['label']}\">\n"
        for opt in entry["options"]:
            selected = ' selected="selected"' if opt["id"] == apid else ""
            s += (
                f"<option value=\"{opt['id']}\"{selected}>{opt['label']} "
                f"(#{opt['id']})</option>\n"
            )
        s += "</optgroup>\n"

    s += "</select>\n"
    return s


def generate_overview(apid):
    """If we don't have an apid set (==0), then fill in the overview."""
    if apid > 0:
        return ""
    return f"""
<h1>Visual Overview of All Autoplots</h1>

<p>Below you will find an example resulting image from each of the autoplots
available.  Click on the image or title to navigate to that autoplot. These are
grouped into sections as they also appear grouped in the dropdown selection
box above.</p>

    {open("/mesonet/share/pickup/autoplot/overview.html").read()}
    """


def generate(fdict, headers, cookies):
    """Return a dict of things for the template engine."""
    apid = int(fdict.get("q", 0))
    res = generate_form(apid, fdict, headers, cookies)
    content = f"""
<h3>Automated Data Plotter</h3>

<p>This application dynamically generates many types of graphs.  These graphs
are derived from processing of various data sources done by the IEM.  Please
feel free to use these generated graphics in whatever way you wish.</p>

<br /><form method="GET" name="t">
<div class="form-group">
<h4><span class="fa fa-arrow-right"></span> First, select a chart type::</h4>
{generate_autoplot_list(apid)}
<input type="submit" value="Select Plot Type" />
</div>
</form>

<hr />

{res["formhtml"]}

{res['description']}

<hr>

{res["image"]}

{res["dataextra"]}

{res["issues"]}

{generate_overview(apid)}

    """
    return {
        "title": "Automated Data Plotter",
        "content": content,
        "jsextra": f"""
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script
 src="/vendor/jquery-ui-timepicker/1.6.3/jquery-ui-timepicker-addon.min.js">
</script>
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
{res['extrascripts']}
<script>
function hideImageLoad(){{
        // console.log("load() fired...");
        $('#willload').css('display', 'none');
}}
$(document).ready(function(){{
    {res['jsextra']}
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
 href="/vendor/jquery-ui-timepicker/1.6.3/jquery-ui-timepicker-addon.min.css"/
 >
 <link rel="stylesheet" type="text/css"
 href="/vendor/select2/4.0.3/select2.min.css"/ >
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
 {res['headextra']}
        """,
    }


def application(environ, start_response):
    """mod-wsgi handler."""
    fdict = parse_formvars(environ)
    cookies = get_cookie_dict(environ)
    headers = [("Content-type", "text/html")]
    tdict = generate(fdict, headers, cookies)
    start_response("200 OK", headers)
    return [TEMPLATE.render(tdict).encode("utf-8")]
