<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 40);
require_once "../../include/myview.php";
require_once "../../include/mlib.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";
require_once "../../include/station.php";

$t = new MyView();

$sortcol = isset($_GET["sortcol"]) ? xssafe($_GET["sortcol"]) : "peak";
$metar = isset($_GET["metar"]) ? xssafe($_GET['metar']) : "no";
$sorder = isset($_GET["sorder"]) ? xssafe($_GET["sorder"]) : "desc";
$wfo = isset($_REQUEST["wfo"]) ? xssafe($_REQUEST["wfo"]) : 'DMX';

$t->refresh = 60;
$t->title = "Obs by NWS Forecast Office";
$nt = new NetworkTable("WFO");
if (!key_exists($wfo, $nt->table)){
    xssafe("<script>");
}
$tzname = $nt->table[$wfo]["tzname"];
$tzinfo = new DateTimeZone($tzname);

$arr = array(
    "wfo" => $wfo,
);
$jobj = iemws_json("currents.json", $arr);

$vals = array(
    "tmpf" => "Air Temperature [F]", "dwpf" => "Dew Point Temp [F]",
    "sknt" => "Wind Speed [knots]", "drct" => "Wind Direction [deg]",
    "alti" => "Altimeter [mb]", "peak" => "Today's Wind Gust [knots]",
    "peak_ts" => "Time of Peak Gust", "relh" => "Relative Humidity",
    "feel" => "Feels Like [F]", "vsby" => "Visibility [miles]",
    "ts" => "Observation Time", "phour" => "Last Hour Rainfall [inch]",
    "min_tmpf" => "Today's Low Temperature",
    "max_tmpf" => "Today's High Temperature",
    "pday" => "Today Rainfall [inch]"
);

$t->current_network = "By NWS WFO";

$wselect = "<select name=\"wfo\">";
foreach ($nt->table as $key => $value) {
    $wselect .= "<option value=\"$key\" ";
    if ($wfo == $key) $wselect .= "SELECTED";
    $wselect .= ">[" . $key . "] " . $nt->table[$key]["name"] . "</option>\n";
}
$wselect .= "</select>";

$mydata = array();
foreach ($jobj["data"] as $bogus => $iemob) {
    $key = $iemob["station"];
    $mydata[$key] = $iemob;
    $valid = new DateTime($mydata[$key]["utc_valid"], new DateTimeZone("UTC"));
    $lts = $valid->setTimezone($tzinfo);
    $mydata[$key]["ts"] = $lts->format("YmdHi");
    $mydata[$key]["lts"] = $lts;
    $mydata[$key]["sped"] = $mydata[$key]["sknt"] * 1.15078;
    $mydata[$key]["relh"] = relh(f2c($mydata[$key]["tmpf"]), f2c($mydata[$key]["dwpf"]));

    if ($mydata[$key]["max_gust"] > $mydata[$key]["max_sknt"]) {
        $mydata[$key]["peak"] = $mydata[$key]["max_gust"];
        $mydata[$key]["peak_ts"] = null;
        if (! is_null($mydata[$key]["utc_max_gust_ts"])) {
            $gts = new DateTime($mydata[$key]["utc_max_gust_ts"], new DateTimeZone("UTC"));
            $mydata[$key]["peak_ts"] = $gts->setTimezone($tzinfo);
        }
    } else {
        $mydata[$key]["peak"] = $mydata[$key]["max_sknt"];
        $mydata[$key]["peak_ts"] = null;
        if (! is_null($mydata[$key]["local_max_sknt_ts"])) {
            $gts = new DateTime($mydata[$key]["utc_max_sknt_ts"], new DateTimeZone("UTC"));
            $mydata[$key]["peak_ts"] = $gts->setTimezone($tzinfo);
        }
    }
}

$table = "";
$finalA = aSortBySecondIndex($mydata, $sortcol, $sorder);
$now = new DateTime("now", new DateTimeZone("UTC"));
$now = $now->setTimezone($tzinfo);
$i = 0;
foreach ($finalA as $key => $parts) {
    $i++;
    $table .= "<tr";
    if ($i % 2 == 0)  $table .= " bgcolor='#eeeeee'";
    $table .= "><td><input type=\"checkbox\" name=\"st[]\" value=\"" . $key . "\"></td>";

    $tdiff = $now->getTimestamp() - $parts["lts"]->getTimestamp();
    $moreinfo = sprintf("/sites/site.php?station=%s&network=%s", $key, $parts["network"]);
    $table .= "<td>" . $parts["name"] . " (<a href=\"$moreinfo\">" . $key . "</a>," . $parts["network"] . ")</td>";
    $table .= "<td ";
    if ($tdiff > 10000) {
        $fmt = "d M h:i A";
        $table .= 'bgcolor="red"';
    } else if ($tdiff > 7200) {
        $fmt = "h:i A";
        $table .= 'bgcolor="orange"';
    } else if ($tdiff > 3600) {
        $fmt = "h:i A";
        $table .= 'bgcolor="green"';
    } else {
        $fmt = "h:i A";
    }
    $table .= ">" . $parts["lts"]->format($fmt) . "</td>
     <td align='center'>" . myround($parts["tmpf"], 0) . "(<font color=\"#ff0000\">" . myround($parts["max_tmpf"], 0) . "</font>/<font color=\"#0000ff\">" . myround($parts["min_tmpf"], 0) . "</font>)</td>
     <td>" . myround($parts["dwpf"], 0) . "</td>
     <td>" . myround($parts["feel"], 0) . "</td>
        <td>" . $parts["relh"] . "</td>
        <td>" . $parts["alti"] . "</td>
        <td>" . $parts["vsby"] . "</td>
             <td>" . myround($parts["sknt"], 0);
    if (strlen($parts["gust"] != 0)) {
        $table .= "G" . myround($parts["gust"], 0);
    }
    $table .= "</td>";
    $aa = is_null($parts["peak_ts"]) ? "" : $parts["peak_ts"]->format("h:i A");
    $phour = ($parts["phour"] != 0.0001) ? $parts["phour"] : 'T';
    $pday = ($parts["pday"] != 0.0001) ? $parts["pday"] : 'T';
    $table .= "<td>" . $parts["drct"] . "</td>
        <td>" . myround($parts["peak"], 0) . " @ {$aa}</td>
            <td>{$phour}</td>
            <td>{$pday}</td>
        </tr>\n";
    if ($metar == "yes") {
        $table .= "<tr";
        if ($i % 2 == 0)  $table .= " bgcolor='#eeeeee'";
        $table .= ">";
        $table .= "<td colspan=14 align=\"CENTER\">
             <font color=\"brown\">" . $parts["raw"] . "</font></td>
             </tr>\n";
    }
}
$uri = "obs.php?wfo=$wfo&metar=$metar&sorder=$sorder&sortcol=";

$ar = array("no" => "No", "yes" => "Yes");
$mselect = make_select("metar", $metar, $ar);

$ar = array("asc" => "Ascending", "desc" => "Descending");
$sselect = make_select("sorder", $sorder, $ar);

$t->content = <<<EOF
<form method="GET" action="obs.php" name="work">
<input type="hidden" value="{$sortcol}" name="sortcol">

<div class="row">
<div class="col-md-5">
  <strong>Select WFO:</strong> {$wselect}
</div>
<div class="col-md-3">
  <strong>Include METARS:</strong> {$mselect}
</div>
<div class="col-md-3">
  <strong>Sort Order:</strong> {$sselect}
</div>
<div class="col-md-1">
  <input type="submit" value="Go!">
</div>
</div>

</form>

<p>Sorted by column <b>{$vals[$sortcol]}</b>. 
Timestamps displayed are for <strong>{$tzname}</strong> timezone.

<form method="GET" action="/my/current.phtml">

<table class="table table-striped table-condensed table-bordered">
<thead class="sticky">
<tr>
  <th rowspan="2">ADD:</th>
  <th rowspan="2">Station:</th>
  <th rowspan="2"><a href="{$uri}ts">Ob Time</a></th>
  <th colspan="3">Temps &deg;F</th>
  <th colspan="3">&nbsp;</th>
  <th colspan="3">Wind [knots]</th>
  <th colspan="2">Precip</font></th>
<tr>
  <th>
 <a href="{$uri}tmpf">Air</a>
 (<a href="{$uri}max_tmpf">Hi</a> /
 <a href="{$uri}min_tmpf">Lo</a>)
</th>
  <th><a href="{$uri}dwpf">Dewp</a></th>
  <th><a href="{$uri}feel">Feels Like</a></th>
  <th><a href="{$uri}relh">RH %</a></th>
  <th><a href="{$uri}alti">Alti</a></th>
  <th><a href="{$uri}vsby">Vsby</a></th>
  <th><a href="{$uri}sknt">Speed</a></th>
  <th><a href="{$uri}drct">Direction</a></th>
  <th><a href="{$uri}peak">Gust</a>
    @ <a href="{$uri}peak_ts">Time</a></th>
  <th><a href="{$uri}phour">Last Hour</a></th>
  <th><a href="{$uri}pday">Today</a></th>
</tr></thead>
<tbody>  
{$table}
</tbody>
</table>

<input type="submit" value="Add to Favorites">
<input type="reset" value="Reset">

</form></div>
EOF;
$t->render("sortables.phtml");
