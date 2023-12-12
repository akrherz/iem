<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";
require_once "../../include/mlib.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$t = new MyView();
$t->refresh = 60;
$t->title = "Latest Observation";
$t->sites_current = "current";
$SPECIAL = array(
    'OT0013' => 'MCFC-001',
    'OT0014' => 'MCFC-002',
    'OT0015' => 'MCFC-003'
);
$LOOKUP = array(
    'OT0013' => 'scranton',
    'OT0014' => 'carroll',
    'OT0015' => 'jefferson'
);
function fmt($val, $varname)
{
    if ($varname == 'altimeter[in]') {
        return sprintf("%.2f", $val);
    }
    return $val;
}
function make_shef_table($data, $iscurrent){
    global $shefcodes, $durationcodes, $extremumcodes, $metadata;
    $msg = $iscurrent ? "Recent": "Five days and older";
    $table = <<<EOM
    <p><strong>{$msg} SHEF encoded data</strong></p>
    <table class="table table-striped">
    <thead class="sticky">
        <tr><th>Physical Code</th><th>Duration</th><th>Type</th>
        <th>Source</th><th>Extrenum</th><th>Valid</th><th>Value</th>
        <th>Product</th></tr>
    </thead>
    EOM;
    $localtz = new DateTimeZone($metadata["tzname"]);
    $utctz = new DateTimeZone("UTC");
    $baseprodvalid = new DateTime("now", $utctz);
    $baseprodvalid->modify("-5 days");
    foreach ($data as $bogus => $row) {
        $depth = "";
        if ($row["depth"] > 0) {
            $depth = sprintf("%d inch", $row["depth"]);
        }
        $valid = new DateTime($row["utc_valid"], $utctz);
        $valid->setTimezone($localtz);
        $plink = "N/A";
        if ($iscurrent && $valid < $baseprodvalid){
            continue;
        }
        if (! $iscurrent && $valid >= $baseprodvalid){
            continue;
        }
        if ($valid > $baseprodvalid) {
            if (!is_null($row["product_id"])) {
                $plink = sprintf(
                    '<a href="/p.php?pid=%s">Source Text</a>',
                    $row["product_id"]
                );
            }
        }
        $table .= sprintf(
            "<tr><td>[%s] %s %s</td><td>[%s] %s</td><td>%s</td>" .
                "<td>%s</td><td>[%s] %s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
            $row["physical_code"],
            array_key_exists($row["physical_code"], $shefcodes) ? $shefcodes[$row["physical_code"]] : "((unknown code))",
            $depth,
            $row["duration"],
            $durationcodes[$row["duration"]],
            $row["type"],
            $row["source"],
            $row["extremum"] == 'Z' ? '-' : $row['extremum'],
            $extremumcodes[$row["extremum"]],
            $valid->format("M j, Y h:i A"),
            $row["value"],
            $plink
        );
    }
    $table .= "</table>";
    return $table;
}

if (strpos($network, "_DCP") || strpos($network, "_COOP")) {
    $table = <<<EOM
<p>This station reports observations in SHEF format. The following two tables
break these SHEF reports into recently made reports and those older than five
days ago.  The IEM's archive of raw SHEF text products is only five days, so
thus why the Product links are only for the first table.
EOM;
    $mesosite = iemdb('mesosite');
    $shefcodes = array();
    $rs = pg_query($mesosite, "SELECT * from shef_physical_codes");
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $shefcodes[$row['code']] = $row['name'];
    }
    $durationcodes = array();
    $rs = pg_query($mesosite, "SELECT * from shef_duration_codes");
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $durationcodes[$row['code']] = $row['name'];
    }
    $extremumcodes = array();
    $rs = pg_query($mesosite, "SELECT * from shef_extremum_codes");
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $extremumcodes[$row['code']] = $row['name'];
    }
    $arr = array(
        "station" => $station,
    );
    $jobj = iemws_json("last_shef.json", $arr);
    $exturi = sprintf(
        "https://mesonet.agron.iastate.edu/api/1/last_shef.json?" .
            "station=%s",
        $station,
    );
    $table .= make_shef_table($jobj["data"], TRUE);
    $table .= make_shef_table($jobj["data"], FALSE);

} else {
    $wsuri = sprintf(
        "http://iem.local/json/current.py?network=%s&station=%s",
        $network,
        $station
    );
    $exturi = sprintf(
        "https://mesonet.agron.iastate.edu/" .
            "json/current.py?network=%s&station=%s",
        $network,
        $station
    );
    $data = file_get_contents($wsuri);
    $json = json_decode($data, $assoc = TRUE);

    $vardict = array(
        "local_valid" => "Observation Local Time",
        "utc_valid" => "Observation UTC Time",
        "airtemp[F]" => "Air Temp [F]",
        "max_dayairtemp[F]" => "Maximum Air Temperature [F]",
        "min_dayairtemp[F]" => "Minimum Air Temperature [F]",
        "dewpointtemp[F]" => "Dew Point [F]",
        "relh" => "Relative Humidity [%]",
        "winddirection[deg]" => "Wind Direction",
        "windspeed[kt]" => "Wind Speed [knots]",
        "srad" => "Solar Radiation",
        "altimeter[in]" => "Altimeter [inches]",
        "pday" => "Daily Precipitation [inches]",
        "pmonth" => "Monthly Precipitation [inches]",
        "gust" => "Wind Gust [knots]",
        "c1tmpf" => "Soil Temperature [F]",
        "c2tmpf" => "Soil Temperature [F]",
        "c3tmpf" => "Soil Temperature [F]",
        "c4tmpf" => "Soil Temperature [F]",
        "c5tmpf" => "Soil Temperature [F]",
        "c1smv" => "Soil Moisture [%]",
        "c2smv" => "Soil Moisture [%]",
        "c3smv" => "Soil Moisture [%]",
        "c4smv" => "Soil Moisture [%]",
        "c5smv" => "Soil Moisture [%]",
        "srad_1h[J m-2]" => "Solar Radiation [past 60 minutes] [J m-2]",
        "tsoil[4in][F]" => "Soil Temperature [4 inch / 10 cm] [F]",
        "tsoil[8in][F]" => "Soil Temperature [8 inch / 20 cm] [F]",
        "tsoil[16in][F]" => "Soil Temperature [16 inch / 40 cm] [F]",
        "tsoil[20in][F]" => "Soil Temperature [20 inch / 50 cm] [F]",
        "tsoil[32in][F]" => "Soil Temperature [32 inch / 80 cm] [F]",
        "tsoil[40in][F]" => "Soil Temperature [40 inch / 100 cm] [F]",
        "tsoil[64in][F]" => "Soil Temperature [64 inch / 160 cm] [F]",
        "tsoil[128in][F]" => "Soil Temperature [128 inch / 320 cm] [F]",
        "raw" => "Raw Observation/Product"
    );

    if ($network == 'ISUSM') {
        $vardict["c1tmpf"] = "4 inch Soil Temperature [F]";
        $vardict["c2tmpf"] = "12 inch Soil Temperature [F]";
        $vardict["c3tmpf"] = "24 inch Soil Temperature [F]";
        $vardict["c4tmpf"] = "50 inch Soil Temperature [F]";
        $vardict["c2smv"] = "12 inch Soil Moisture [%]";
        $vardict["c3smv"] = "24 inch Soil Moisture [%]";
        $vardict["c4smv"] = "50 inch Soil Moisture [%]";
    }

    $table = "<table class=\"table table-striped\">";
    foreach ($vardict as $key => $label) {
        if (
            is_null($json) ||
            !array_key_exists("last_ob", $json) ||
            !array_key_exists($key, $json["last_ob"])
        ) {
            continue;
        }
        if ($key == "local_valid") {
            $t2 = date("d M Y, g:i A", strtotime($json["last_ob"][$key]));
            $table .= '<tr><td><b>' . $label . '</b></td><td>' . $t2 . '</td></tr>';
        } else if ($key == "winddirection[deg]") {
            $table .= sprintf(
                "<tr><td><b>%s</b></td><td>%s (%.0f degrees)</td></tr>",
                $label,
                drct2txt($json["last_ob"][$key]),
                $json["last_ob"][$key]
            );
        } else {
            if (is_null($json["last_ob"][$key])) continue;
            $table .= '<tr><td><b>' . $label . '</b></td>' .
                '<td>' . fmt($json["last_ob"][$key], $key) . '</td></tr>';
        } // End if
    } // End if
    $table .= "</table>";

    // Cloud Levels
    $skyc = $json["last_ob"]["skycover[code]"];
    $skyl = $json["last_ob"]["skylevel[ft]"];
    for ($i = 0; $i < 4; $i++) {
        if (is_null($skyc[$i])) continue;
        $table .= sprintf(
            "<b>Cloud Layer %s</b>: %s (%s feet)<br />",
            $i + 1,
            $skyc[$i],
            $skyl[$i]
        );
    }
}

$table .= sprintf("<p>This data was provided by a " .
    "<a href=\"%s\">JSON(P) webservice</a>. You can find " .
    "<a href=\"/json/\">more JSON services</a>.</p>", $exturi);

$interface = $table;
if (array_key_exists($station, $SPECIAL)) {
    $interface = <<<EOM
<h4>New Way Weather Network</h4>

<a class="btn btn-default" href="/sites/current.php?station=OT0013&network=OT">Scranton</a>
&nbsp;
<a class="btn btn-default" href="/sites/current.php?station=OT0014&network=OT">Carroll</a>
&nbsp;
<a class="btn btn-default" href="/sites/current.php?station=OT0015&network=OT">Jefferson</a>

<div class="row">
  <div class="col-md-6">
    {$table}
  </div>
  <div class="col-md-6">
    <h3>Latest Webcam Image</h3>
    <img src="/data/camera/stills/{$SPECIAL[$station]}.jpg"
     class="img img-responsive">
    <br />View Recent Time Lapses:<br />
    <a href="/current/camlapse/#{$LOOKUP[$station]}_sunrise">Sunrise</a>,
    <a href="/current/camlapse/#{$LOOKUP[$station]}_morning">Morning</a>,
    <a href="/current/camlapse/#{$LOOKUP[$station]}_afternoon">Afternoon</a>,
    <a href="/current/camlapse/#{$LOOKUP[$station]}_sunset">Sunset</a>, and
    <a href="/current/camlapse/#{$LOOKUP[$station]}_day">All Day</a>
  </div>
</div>

EOM;
}

$t->content = <<<EOF

<h3>Most Recent Observation</h3>

<p>This application displays the last observation received by the IEM
 from this site. The time stamp is in 
 <strong>{$metadata["tzname"]}</strong> timezone.</p>

{$interface}

EOF;
$t->render('sites.phtml');
