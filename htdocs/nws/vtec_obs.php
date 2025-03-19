<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 108);
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/mlib.php";
require_once "../../include/network.php";
require_once "../../include/imagemaps.php";

$nt = new NetworkTable("WFO");
$t = new MyView();
$wfo = isset($_REQUEST["wfo"]) ? xssafe($_REQUEST["wfo"]) : 'DMX';
$wfo3 = unrectify_wfo($wfo);
$year = get_int404("year", date("Y"));
if ($year < 1986) xssafe("<script>");
$sid = get_int404("sid", 1);
$eid = get_int404("eid", 999);
$rhthres = isset($_REQUEST["relh"]) ? floatval(xssafe($_REQUEST["relh"])) : 25;
$skntthres = isset($_REQUEST["sknt"]) ? floatval(xssafe($_REQUEST["sknt"])) : 25;
$gustthres = isset($_REQUEST["gust"]) ? floatval(xssafe($_REQUEST["gust"])) : 25;
$vsbythres = isset($_REQUEST["vsby"]) ? floatval(xssafe($_REQUEST["vsby"])) : 0.25;
$ltmpfthres = isset($_REQUEST["ltmpf"]) ? floatval(xssafe($_REQUEST["ltmpf"])) : 32;
$wchtthres = isset($_REQUEST["wcht"]) ? floatval(xssafe($_REQUEST["wcht"])) : -20;
$hidxthres = isset($_REQUEST["hidx"]) ? floatval(xssafe($_REQUEST["hidx"])) : 105;
$htmpfthres = isset($_REQUEST["htmpf"]) ? floatval(xssafe($_REQUEST["htmpf"])) : 100;
$mode = isset($_REQUEST["mode"]) ? substr(xssafe($_REQUEST["mode"]), 0, 4) : 'FW.W';
$ar = explode(".", $mode);
$phenomena = $ar[0];
$significance = $ar[1];

$t->title = "NWS Watch/Warning/Advisory + ASOS Observations";

$ar = array(
    "BZ.W" => "Blizzard Warning",
    "FG.Y" => "Dense Fog Advisory",
    "EH.W" => "Extreme Heat Warning",
    "FR.Y" => "Frost Advisory",
    "FZ.W" => "Freeze Warning",
    "HZ.W" => "Hard Freeze Warning",
    "HT.Y" => "Heat Advisory",
    "HW.W" => "High Wind Warning",
    "FW.W" => "Red Flag Warning",
    "WI.Y" => "Wind Advisory",
    "WC.Y" => "Wind Chill Advisory",
    "WC.W" => "Wind Chill Warning",
);
$mselect = make_select("mode", $mode, $ar);
$wselect = "<select name=\"wfo\">\n";
foreach ($nt->table as $key => $value) {
    $wselect .= "<option value=\"$key\" ";
    if ($wfo == $key) $wselect .= "SELECTED";
    $wselect .= ">[" . $key . "] " . $nt->table[$key]["name"] . "\n";
}
$wselect .= "</select>";
$yselect = yearSelect(2005, $year);

$postgis = iemdb("postgis");
$asos = iemdb("asos");
pg_query($postgis, "SET TIME ZONE 'UTC'");
pg_query($asos, "SET TIME ZONE 'UTC'");

$find_stname = iem_pg_prepare(
    $postgis,
    "SELECT string_agg(ugc::text, ',') as a, eventid, issue, " .
        "expire from warnings_$year WHERE wfo = $1 and phenomena =  $4 and " .
        "significance = $5 and eventid >= $2 and eventid < $3 " .
        "GROUP by issue, expire, eventid ORDER by issue ASC"
);

$station2ugc = array();
$ugc2station = array();
$stname = iem_pg_prepare($postgis, "SELECT id, ugc_zone from stations " .
    "where wfo = $1 and network ~* 'ASOS'");
$rs = pg_execute($postgis, $stname, array($wfo3));
while ($row = pg_fetch_assoc($rs)) {
    if (!array_key_exists($row["ugc_zone"], $ugc2station)) {
        $ugc2station[$row["ugc_zone"]] = array();
    }
    $ugc2station[$row["ugc_zone"]][] = $row["id"];
    $station2ugc[$row["id"]] = $row["ugc_zone"];
}

function c1($relh)
{
    global $rhthres;
    if ($relh >= $rhthres) {
        return sprintf("%.0f%%", $relh);
    }
    return sprintf("<span style='color:#f00;'>%.0f%%</span>", $relh);
}

function c2($sknt, $gust)
{
    global $skntthres;
    global $gustthres;
    $s = "";
    $a = False;
    if ($sknt < $skntthres) {
        $s .= $sknt;
    } else {
        $a = True;
        $s .= sprintf("<span style='color:#f00;'>%s</span>", $sknt);
    }

    if ($gust < $gustthres) {
        $s .= sprintf("/%s", $gust);
    } else {
        $a = True;
        $s .= sprintf("/<span style='color:#f00;'>%s</span>", $gust);
    }
    if ($a) {
        return sprintf("%s<span style='color:#f00;'>KT</span>", $s);
    } else {
        return sprintf("%sKT", $s);
    }
}

function c3($vsby)
{
    if (is_null($vsby)) return "MMSM";
    global $vsbythres;
    if ($vsby <= $vsbythres) {
        return sprintf("<span style='color:#f00;'>%.1fSM</span>", $vsby);
    }
    return sprintf("%.1fSM", $vsby);
}
function c4($tmpf)
{
    if (is_null($tmpf)) return "M";
    global $ltmpfthres;
    global $htmpfthres;
    if ($tmpf <= $ltmpfthres) {
        return sprintf("<span style='color:#00f; font-weight:bold;'>%.0f</span>", $tmpf);
    }
    if ($tmpf >= $htmpfthres) {
        return sprintf("<span style='color:#f00;'>%.0f</span>", $tmpf);
    }
    return sprintf("%.0f", $tmpf);
}
function c5($wcht)
{
    if (is_null($wcht))  return "";
    global $wchtthres;
    if ($wcht <= $wchtthres)
        return sprintf(
            "<span style='color:#00f; font-weight:bold;'> WC %.0f</span>",
            $wcht
        );
    if ($wcht < 32)
        return sprintf(" WC %.0f", $wcht);
    return "";
}
function c6($hidx, $thres)
{
    if (is_null($hidx))  return "";
    if ($hidx >= $thres)
        return sprintf(
            "<span style='color:#f00; font-weight:bold;'> HIDX %.0f</span>",
            $hidx
        );
    if ($hidx > 80)
        return sprintf(" HIDX %.0f", $hidx);
    return "";
}

$table = "";

$rs = pg_execute($postgis, $find_stname, array(
    $wfo3, $sid, $eid, $phenomena,
    $significance
));
if ($rs === FALSE) xssafe("<tag>");
for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    $ar = explode(",", $row["a"]);
    $issue = $row["issue"];
    $expire = $row["expire"];
    $eventid = $row["eventid"];
    $stations = "(";

    $table .= sprintf(
        "<h3>Event: %s Issue: %s Expire: %s</h3>\n",
        $eventid,
        $issue,
        $expire
    );
    $table .= "<p><strong>UGC Codes:</strong> ";
    foreach ($ar as $k => $zone) {
        $table .= " $zone,";
        if (array_key_exists($zone, $ugc2station)) {
            foreach ($ugc2station[$zone] as $k2 => $st) {
                $stations  .= sprintf("'%s',", $st);
            }
        }
    }
    $stations .= "'ZZZZZ')";
    $table .= "<p><strong>ASOS/AWOS IDs:</strong> ";
    $table .= str_replace(",'ZZZZZ'", "", $stations);
    $table .= "<br />";
    $rs2 = pg_query(
        $asos,
        "SELECT station, valid, to_char(valid, 'ddHH24MI') as z, " .
            "tmpf, dwpf, sknt, gust, vsby, feel from alldata " .
            "WHERE valid BETWEEN '$issue' and '$expire' and " .
            "station in $stations and report_type != 1 " .
            "ORDER by station, valid ASC"
    );
    $table .= "<table class=\"table table-condensed\">";
    $ostation = "";
    $stfound = 0;
    for ($j = 0; $row2 = pg_fetch_assoc($rs2); $j++) {
        if ($ostation != $row2["station"]) {
            if ($stfound > 0 && $stfound % 3 == 0) {
                $table .= "</td></tr>";
                $ostation = "";
            }
            if ($ostation == "") $table .= "<tr><td valign='top'>";
            else $table .= "</td><td valign='top'>";
            $ostation = $row2["station"];
            $stfound += 1;
            $table .= sprintf("<u>UGC Code: %s</u><br/>", $station2ugc[$row2["station"]]);
        }
        $table .= sprintf(
            "%s %sZ %s/%.0f %s %s %s%s%s<br>",
            $row2["station"],
            $row2["z"],
            c4($row2["tmpf"]),
            $row2["dwpf"],
            c1(relh(f2c($row2["tmpf"]), f2c($row2["dwpf"]))),
            c3($row2["vsby"]),
            c2($row2["sknt"], $row2["gust"]),
            c5($row2["feel"]),
            c6($row2["feel"], $hidxthres),
        );
    }
    $table .= "</td></tr></table>";
}

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="current">NWS Watch/Warning/Advisory + ASOS Observations</li>
</ol>
  
  <p>This app allows you to view an office's warnings for a year and
  then looks for ASOS/AWOS observations valid for the warning period. The observations
  presented are coded like:
  <br /><code>ID DDHHMI TMPF/DWPF RELH VSBY SKNT/GUST WC WINDCHILL HIDX HEAT INDEX</code>
  <br />Where ID is the station identifier, DDHHMI is the day-hour-minute of the
  observation in UTC, TMPF is the air temperature in Fahrenheit, DWPF is the
  dew point temperature in Fahrenheit, RELH is the relative humidity, VSBY is
  the visibility, SKNT is the wind speed in knots and GUST is the wind gust in knots. 
  The wind chill is displayed when the temperature is below 32&deg;F. The heat index
  is displayed when the value is above 80&deg;F.
  
  <p>A warning event may be listed multiple times, if the UGC zones associated 
  with the warning had different expiration times.
    
  <form method="GET" name="theform">
  
  <p>
  <table class="table table-condensed">
  <tr>
    <th>WWA Type:</th>
    <th>Start Event ID:</th>
    <th>End Event ID:</th>
    <th>Select WFO:</th>
      <th>Select Year:</th>
      </tr>
      <tr>
      <td>{$mselect}</td>
      <td><input type="text" size="10" name="sid" value="{$sid}" /></td>
      <td><input type="text" size="10" name="eid" value="{$eid}" /></td>
      <td>{$wselect}</td>
    <td>{$yselect}</td>
    </tr>
    </table>
  
  <table class="table table-condensed">
  <tr>	
      <th>Relative Humidity Threshold (%):</th>
      <th>Wind Speed Threshold (kts):</th>
      <th>Wind Gust Threshold (kts):</th>
      <th>Visibility Threshold (mile):</th>
    </tr>
    <tr>
    <td><input type="text" size="10" name="relh" value="{$rhthres}" /></td>
    <td><input type="text" size="10" name="sknt" value="{$skntthres}" /></td>
    <td><input type="text" size="10" name="gust" value="{$gustthres}" /></td>
    <td><input type="text" size="10" name="vsby" value="{$vsbythres}" /></td>
    </tr>
  <tr>
    <th>Air Temperatures below... (F):</th>
    <th>Air Temperatures above... (F):</th>
    <th>Wind Chill Below... (F)</th>
    <th>Heat Index Above...(F)</th>
  </tr>
    <tr>
    <td><input type="text" size="10" name="ltmpf" value="{$ltmpfthres}" /></td>
    <td><input type="text" size="10" name="htmpf" value="{$htmpfthres}" /></td>
    <td><input type="text" size="10" name="wcht" value="{$wchtthres}" /></td>
    <td><input type="text" size="10" name="hidx" value="{$hidxthres}" /></td>
    <td></td>
    </tr>
    </table>
    <input type="submit" value="Generate Report"/>
  </form>

{$table}
EOM;
$t->render('full.phtml');
