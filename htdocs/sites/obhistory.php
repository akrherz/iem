<?php
// This app apparently is an AI bot playground, so this setting causes the
// downstream throttle to be more aggressive
define("THROTTLE_APP", "sites/obhistory");
require_once "../../include/sites.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

/*
 * Rip off weather bureau website, but do it better
 */
function wind_formatter($row, $units = "mph")
{
    if (is_null($row["drct"]) && is_null($row["sknt"])) {
        return "M";
    }

    // Convert knots to appropriate units
    $multiplier = ($units == "mph") ? 1.15 : 1.0; // knots to mph conversion factor

    if (is_null($row["drct"]) && ($row["sknt"] > 0) && ($row["sknt"] < 10)) {
        return sprintf("VRB %.0f", $row["sknt"] * $multiplier);
    }
    if (($row["drct"] == 0) && ($row["sknt"] == 0)) {
        return "Calm";
    }
    if (is_null($row["drct"])) {
        return "M";
    }
    $gust_text = "";
    if ($row["gust"] > 0) {
        $gust_text = sprintf("G%.0f", $row["gust"] * $multiplier);
    }
    $peak_text = "";
    if (!is_null($row["peak_wind_gust"]) &&
        !is_null($row["peak_wind_drct"]) &&
        !is_null($row["peak_wind_time"])) {
        $peakdt = new DateTime($row["peak_wind_time"],
            new DateTimeZone("UTC"));
        global $metadata;
        $peaktime = $peakdt->setTimezone(new DateTimeZone($metadata["tzname"]))
            ->format("g:i A");
        $peak_text = sprintf(
            "<br />PK %s %.0f @ %s",
            drct2txt($row["peak_wind_drct"]),
            $row["peak_wind_gust"] * $multiplier,
            $peaktime,
        );
    }
    return sprintf(
        "%s %.0f%s%s",
        drct2txt($row["drct"]),
        $row["sknt"] * $multiplier,
        $gust_text,
        $peak_text,
    );
}
function indy_sky_formatter($skyc, $skyl)
{
    if (intval($skyl) > 0) {
        $skyl = sprintf("%03d", $skyl / 100);
    } else {
        $skyl = "";
    }
    if (is_null($skyc) || trim($skyc) == "") return "";
    return sprintf("%s%s<br />", $skyc, $skyl);
}
function sky_formatter($row)
{
    return sprintf(
        "%s%s%s%s",
        indy_sky_formatter($row["skyc1"], $row["skyl1"]),
        indy_sky_formatter($row["skyc2"], $row["skyl2"]),
        indy_sky_formatter($row["skyc3"], $row["skyl3"]),
        indy_sky_formatter($row["skyc4"], $row["skyl4"])
    );
}
function temp_formatter($val)
{
    if (is_null($val)) return "";
    return sprintf("%.0f", $val);
}
function vis_formatter($val)
{
    if (is_null($val)) return "";
    return round($val, 2);
}
function precip_formatter($val)
{
    if (is_null($val)) return "";
    if ($val == 0.0001) return "T";
    return round($val, 2);
}
function asos_formatter($i, $row, $windunits = "mph")
{
    $ts = strtotime(substr($row["local_valid"], 0, 16));
    $relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]));
    $relh = (!is_null($relh)) ? intval($relh) : "";
    $ismadis = is_null($row["raw"]) ? FALSE : (strpos($row["raw"], "MADISHF") > 0);
    return sprintf(
        "<tr style=\"background: %s;\" class=\"%sob\" data-madis=\"%s\">" .
            "</div><td>%s</td><td>%s</td><td>%s</td>
    <td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
    <td><span class=\"high\">%s</span></td>
    <td><span class=\"low\">%s</span></td>
    <td>%s</td>
    <td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
    <tr style=\"background: %s;\" class=\"%smetar\">" .
            "<td colspan=\"17\">%s</td></tr>",
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        $ismadis ? "hf" : "",
        $ismadis ? "1" : "0",
        date("g:i A", $ts),
        wind_formatter($row, $windunits),
        vis_formatter($row["vsby"]),
        sky_formatter($row),
        $row["wxcodes"],
        temp_formatter($row["tmpf"]),
        temp_formatter($row["dwpf"]),
        temp_formatter($row["feel"]),
        temp_formatter($row["max_tmpf_6hr"]),
        temp_formatter($row["min_tmpf_6hr"]),
        relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
        $row["alti"],
        $row["mslp"],
        $row["snowdepth"],
        precip_formatter($row["p01i"]),
        precip_formatter($row["p03i"]),
        precip_formatter($row["p06i"]),
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        $ismadis ? " hf" : "",
        $row["raw"]
    );
}
function pavement_formatter($row, $sensor)
{
    $tmp = $row["tfs{$sensor}"];
    $text = $row["tfs{$sensor}_text"];
    return sprintf(
        "%s %s",
        is_null($tmp) ? "" : temp_formatter($tmp),
        is_null($text) ? "" : "($text)"
    );
}
function rwis_formatter($i, $row, $windunits = "mph")
{
    $ts = strtotime(substr($row["local_valid"], 0, 16));
    return sprintf(
        "<tr style=\"background: %s;\">" .
        "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
        "<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        date("g:i A", $ts),
        wind_formatter($row, $windunits),
        temp_formatter($row["tmpf"]),
        temp_formatter($row["dwpf"]),
        temp_formatter($row["feel"]),
        temp_formatter($row["relh"]),
        pavement_formatter($row, 0),
        pavement_formatter($row, 1),
        pavement_formatter($row, 2),
        pavement_formatter($row, 3)
    );
}
function formatter($i, $row, $windunits = "mph")
{
    $ts = strtotime(substr($row["local_valid"], 0, 16));
    $relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]));
    $relh = (!is_null($relh)) ? intval($relh) : "";
    $precip_extra = "";
    if (array_key_exists("phour_flag", $row) && !is_null($row["phour_flag"])) {
        $precip_extra = sprintf(
            " (%s)",
            ($row["phour_flag"] == "E") ? "Estimated" : $row["phour_flag"],
        );
    }
    return sprintf(
        "<tr style=\"background: %s;\">" .
            "<td>%s</td><td>%s</td><td>%s</td>
    <td>%s</td><td>%s</td><td>%s</td><td>%s%s</td></tr>",
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        date("g:i A", $ts),
        wind_formatter($row, $windunits),
        temp_formatter($row["tmpf"]),
        temp_formatter($row["dwpf"]),
        temp_formatter($row["feel"]),
        relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
        precip_formatter($row["phour"]),
        $precip_extra,
    );
}
function hads_formatter($i, $row, $shefcols, $windunits = "mph")
{
    $ts = strtotime(substr($row["local_valid"], 0, 16));
    $relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]));
    $relh = (!is_null($relh)) ? intval($relh) : "";
    $html = "";
    foreach ($shefcols as $bogus => $name) {
        $html .= sprintf("<td>%s</td>", $row["$name"]);
    }
    return sprintf(
        "<tr style=\"background: %s;\">" .
            "<td>%s</td><td>%s</td><td>%s</td>
    <td>%s</td><td>%s</td><td>%s</td><td>%s</td>%s</tr>",
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        date("g:i A", $ts),
        wind_formatter($row, $windunits),
        temp_formatter($row["tmpf"]),
        temp_formatter($row["dwpf"]),
        temp_formatter($row["feel"]),
        relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
        precip_formatter($row["phour"]),
        $html
    );
}
function scan_formatter($i, $row, $windunits = "mph")
{
    $ts = strtotime(substr($row["local_valid"], 0, 16));
    return sprintf(
        "<tr style=\"background: %s;\">" .
            "<td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td></tr>",
        ($i % 2 == 0) ? "#FFF" : "#EEE",
        date("g:i A", $ts),
        wind_formatter($row, $windunits),
        temp_formatter($row["tmpf"]),
        temp_formatter($row["dwpf"]),
        $row["relh"],
        $row["srad"],
        precip_formatter($row["phour"]),
        $row["soilt2"],
        $row["soilm2"],
        $row["soilt4"],
        $row["soilm4"],
        $row["soilt8"],
        $row["soilm8"],
        $row["soilt20"],
        $row["soilm20"],
        $row["soilt40"],
        $row["soilm40"],
    );
}
// Handle both legacy (year/month/day) and modern (date) URL parameters
$date_param = get_str404("date", null);
if (!empty($date_param)) {
    // Modern date parameter takes precedence
    $date_parts = explode("-", $date_param);
    $year = intval($date_parts[0]);
    $month = intval($date_parts[1]);
    $day = intval($date_parts[2]);
} else {
    // Legacy parameters for backwards compatibility
    $year = get_int404("year", date("Y"));
    $month = get_int404("month", date("m"));
    $day = get_int404("day", date("d"));
    $date_param = sprintf("%04d-%02d-%02d", $year, $month, $day);
}

$metar = (get_str404("metar", "0") == "1") ? "1" : "0";
$madis = (get_str404("madis", "0") == "1") ? "1" : "0";
$sortdir = get_str404("sortdir", "asc");
$windunits = get_str404("windunits", "mph");
$date = mktime(0, 0, 0, $month, $day, $year);
$yesterday = $date - 86400;
$tomorrow = $date + 86400;
if ($tomorrow > time()) {
    $tomorrow = null;
}

$sortopts = array(
    "asc" => "Ascending",
    "desc" => "Descending",
);
$sortform = make_select("sortdir", $sortdir, $sortopts);

$windunitopts = array(
    "mph" => "MPH",
    "knots" => "Knots",
);
$windunitform = make_select("windunits", $windunits, $windunitopts);

if (!is_null($metadata["archive_begin"])) {
    $startyear = intval($metadata["archive_begin"]->format("Y"));
} else {
    $startyear = 2010;
}

$t = new MyView();
$t->iemselect2 = true;
$t->title = "Observation History";
$t->sites_current = 'obhistory';

$savevars = array(
    "year" => date("Y", $date),
    "month" => date("m", $date),
    "day" => date("d", $date)
);
$t->jsextra = '<script type="module" src="obhistory.module.js?v=4"></script>';
$t->headextra = '<link rel="stylesheet" href="obhistory.css" type="text/css">';
$dstr = date("d F Y", $date);
$tzname =  $metadata["tzname"];

// Variables for the new date picker UI
$today_param = date("Y-m-d");
$yesterday_param = date("Y-m-d", $yesterday);
$tomorrow_param = ($tomorrow !== null) ? date("Y-m-d", $tomorrow) : null;
$next_disabled = ($tomorrow === null) ? 'disabled' : '';

$ys = yearSelect($startyear, date("Y", $date));
$ms = monthSelect(date("m", $date));
$ds = daySelect(date("d", $date));

$mbutton = (preg_match("/ASOS/", $network)) ?
    '<div class="btn-group-controls">' .
    '<button type="button" class="btn btn-success" id="metar_toggle">' .
    '<i class="bi bi-plus-lg" aria-hidden="true"></i> Show METARs</button>' .
    '<button type="button" class="btn btn-success" id="madis_toggle">' .
    '<i class="bi bi-plus-lg" aria-hidden="true"></i> Show High Frequency MADIS</button>' .
    '</div>'
    : "";

// Legacy navigation buttons are now inline with the date picker
$buttons = "";
$content = <<<EOM
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h3>{$dstr} Observation History, [{$station}] {$metadata["name"]}, timezone: {$tzname}</h3>

            <form id="theform" name="theform" method="GET" class="mb-3">
                <div class="row g-2 align-items-end">
                    <div class="col-auto">
                        <label for="date_picker" class="form-label mb-1">Select Date:</label>
                        <div class="input-group">
                            <button type="button" id="prevbutton" class="btn btn-outline-secondary"
                                data-date="{$yesterday_param}" title="Previous Day">
                                <i class="bi bi-arrow-left" aria-hidden="true"></i>
                            </button>
                            <input type="date" id="date_picker" name="date" class="form-control"
                                value="{$date_param}" min="{$startyear}-01-01" max="{$today_param}">
                            <button type="button" id="nextbutton" class="btn btn-outline-secondary"
                                data-date="{$tomorrow_param}" title="Next Day" {$next_disabled}>
                                <i class="bi bi-arrow-right" aria-hidden="true"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-auto">
                        <label for="sortdir" class="form-label mb-1">Time Order:</label>
                        {$sortform}
                    </div>
                    <div class="col-auto">
                        <label for="windunits" class="form-label mb-1">Wind Units:</label>
                        {$windunitform}
                    </div>
                    <div class="col-auto">
                        <input type="submit" value="Update" class="btn btn-primary" />
                    </div>
                </div>

                <!-- Hidden parameters -->
                <input type="hidden" value="{$station}" name="station" />
                <input type="hidden" value="{$network}" name="network" />
                <input id="hmetar" type="hidden" value="{$metar}" name="metar" />
                <input id="hmadis" type="hidden" value="{$madis}" name="madis" />
            </form>

            {$mbutton}
        </div>
    </div>
</div>
EOM;

$notes = '';
if ($network == "ISUSM") {
    $notes .= "<li>Wind direction and wind speed are 10 minute averages at 10 feet above the ground.</li>";
}

// API endpoint
$errmsg = "";
$arr = array(
    "station" => $station,
    "network" => $network,
    "date" => date("Y-m-d", $date),
    "full" => "1",
);
$wsuri = sprintf("/api/1/obhistory.json?%s", http_build_query($arr));
$jobj = iemws_json("obhistory.json", $arr);
if ($jobj === FALSE) {
    $jobj = array("data" => array(), "schema" => array("fields" => array()));
    $errmsg = "Failed to fetch history from web service. No data was found.";
}

if (preg_match("/ASOS/", $network)) {
    $wind_label = ($windunits == "mph") ? "Wind<br>(mph)" : "Wind<br>(knots)";
    $notes .= <<<EOM
<li>For recent years, this page also optionally shows observations from the
<a href="https://madis.ncep.noaa.gov/madis_OMO.shtml">MADIS High Frequency METAR</a>
dataset.  This dataset had a problem with temperatures detailed <a href="/onsite/news.phtml?id=1290">here</a>.</li>
EOM;
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="3">Time</th>
    <th rowspan="3">{$wind_label}</th>
    <th rowspan="3">Vis.<br>(mi.)</th>
    <th rowspan="3">Sky Cond.<br />(100s ft)</th>
    <th rowspan="3">Present Wx</th>
    <th colspan="5">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th colspan="2">Pressure</th>
    <th rowspan="3">Snow<br />Depth<br />(in)</th>
    <th colspan="3">Precipitation (in.)</th></tr>

    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Air</th>
    <th rowspan="2">Dwpt</th>
    <th rowspan="2">Feels Like</th>
    <th colspan="2">6 hour</th>
    <th rowspan="2">altimeter<br>(in.)</th>
    <th rowspan="2">sea level<br>(mb)</th>
    <th rowspan="2">1 hr</th>
    <th rowspan="2">3 hr</th>
    <th rowspan="2">6 hr</th>
    </tr>

    <tr align="center" bgcolor="#b0c4de"><th>Max.</th><th>Min.</th></tr>
EOM;
} else if (preg_match("/DCP|COOP/", $network)) {
    $wind_label = ($windunits == "mph") ? "Wind<br>(mph)" : "Wind<br>(knots)";
    // Figure out what extra columns we have here.
    $shefcols = array();
    $shefextra = "";
    foreach ($jobj["schema"]["fields"] as $bogus => $field) {
        $name = $field["name"];
        if (preg_match("/^[A-Z]/", $name)) {
            $shefcols[] = $name;
        }
    }
    asort($shefcols);
    $shefheader = sprintf(
        "<th colspan=\"%s\">RAW SHEF CODES</th>",
        sizeof($shefcols)
    );
    foreach ($shefcols as $bogus => $val) {
        $shefextra .= sprintf("<th>%s</th>", $val);
    }
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">{$wind_label}</th>
    <th colspan="3">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th>Precipitation (in.)</th>
    {$shefheader}
    </tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Feels Like</th>
    <th>1 hr</th>
    {$shefextra}
    </tr>
EOM;
} else if (preg_match("/RWIS/", $network)) {
    $wind_label = ($windunits == "mph") ? "Wind<br>(mph)" : "Wind<br>(knots)";
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">{$wind_label}</th>
    <th colspan="3">Temperature (&ordm;F)</th>
    <th rowspan="2">Relative<br>Humidity</th>
    <th colspan="4">Pavement Sensors: Temperature (&ordm;F) (Condition)</th>
    </tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Feels Like</th>
    <th>Sensor 1</th>
    <th>Sensor 2</th>
    <th>Sensor 3</th>
    <th>Sensor 4</th>
    </tr>
EOM;
} else if ($network == "SCAN") {
    $wind_label = ($windunits == "mph") ? "Wind<br>(mph)" : "Wind<br>(knots)";
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">{$wind_label}</th>
    <th colspan="2">Temp (&deg;F)</th>
    <th rowspan="2">RH%</td>
    <th rowspan="2">Solar (W/m2)</th>
    <th rowspan="2">Precipitation (in.)</th>
    <th colspan="2">2 Inch</th>
    <th colspan="2">4 Inch</th>
    <th colspan="2">8 Inch</th>
    <th colspan="2">20 Inch</th>
    <th colspan="2">40 Inch</th>
    </tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Temp</th><th>VWC</th>
    <th>Temp</th><th>VWC</th>
    <th>Temp</th><th>VWC</th>
    <th>Temp</th><th>VWC</th>
    <th>Temp</th><th>VWC</th>
    </tr>
EOM;
} else {
    $wind_label = ($windunits == "mph") ? "Wind<br>(mph)" : "Wind<br>(knots)";
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">{$wind_label}</th>
    <th colspan="3">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th>Precipitation (in.)</th></tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Feels Like</th>
    <th>1 hr</th>
    </tr>
EOM;
}


$table = "";
$i = 0;
$data = $jobj["data"];
if ($sortdir == "desc") {
    $data = array_reverse($data);
}
foreach ($data as $bogus => $row) {
    if (preg_match("/ASOS/", $network)) {
        $table .= asos_formatter($i, $row, $windunits);
    } else if (preg_match("/DCP|COOP/", $network)) {
        $table .= hads_formatter($i, $row, $shefcols, $windunits);
    } else if (preg_match("/RWIS/", $network)) {
        $table .= rwis_formatter($i, $row, $windunits);
    } else if ($network == "SCAN") {
        $table .= scan_formatter($i, $row, $windunits);
    } else {
        $table .= formatter($i, $row, $windunits);
    }
    $i++;
}
$errdiv = "";
if ($errmsg != "") {
    $errdiv = <<<EOM
<div class="alert alert-warning">{$errmsg}</div>
EOM;
}

$content .= <<<EOM

{$errdiv}

<div class="table-container">
    <table class="table table-striped table-bordered table-hover" id="datatable">
    <thead class="sticky">
    {$header}
    </thead>
    <tbody>
    {$table}
    </tbody>
    </table>
</div>

<div class="api-link">
    <p><strong>API:</strong> The <a href="{$wsuri}" target="_blank">IEM API webservice</a> that provided data to this
    page. For more details, see <a href="/api/1/docs#/default/service_obhistory__fmt__get" target="_blank">documentation</a>.</p>
</div>

<div class="data-notes">
    <h4>Data Notes</h4>
    <ul>
    {$notes}
    </ul>
</div>
EOM;
$t->content = $content;
$t->render('sites.phtml');
