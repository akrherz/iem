<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 71);
require_once "../../include/forms.php";
require_once "../../include/mlib.php";
require_once "../../include/myview.php";

$t = new MyView();
$t->title = "River Forecast Point Monitor";
$content = "";

$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]), 0, 3) : "DMX";
$state = isset($_GET["state"]) ? substr(xssafe($_GET["state"]), 0, 2) : "IA";

$sevcol = array(
    "N" => "#0f0",
    "0" => "#ff0",
    "1" => "#ff9900",
    "2" => "#f00",
    "3" => "#f0f",
    "U" => "#fff"
);
$jobs = Array(
    "W" => "warnings",
    "A" => "watches",
);
$c1 = "";
$c2 = "";
$c3 = "";
$rivers = array();
$used = array();
foreach ($jobs as $key => $val) {
    $url = "{$EXTERNAL_BASEURL}/api/1/nws/current_flood_{$val}.json";
    if (isset($_REQUEST["state"])) {
        $c2 = " bg-light border rounded p-3";
        $url .= "?state={$state}";
        $ptitle = "<h3>River Forecast Point Monitor by State</h3>";
    } else if (isset($_REQUEST["all"])) {
        $c3 = " bg-light border rounded p-3";
        $ptitle = "<h3>River Forecast Point Monitor (view all)</h3>";
    } else {
        $c1 = " bg-light border rounded p-3";
        $url .= "?wfo={$wfo}";
        $ptitle = "<h3>River Forecast Point Monitor by NWS WFO</h3>";
    }

    $jdata = file_get_contents($url);
    $jobj = json_decode($jdata, $assoc = TRUE);

    foreach ($jobj["data"] as $bogus => $row) {
        if (in_array($row["nwsli"], $used)) {
            continue;
        }
        $used[] = $row["nwsli"];
        $river = $row["river_name"];
        $uri = sprintf(
            "/vtec/?year=%s&wfo=%s&phenomena=%s&significance=%s&eventid=%s",
            date("Y"),
            rectify_wfo($row["wfo"]),
            $row["phenomena"],
            $row["significance"],
            $row["eventid"]
        );
        if (!array_key_exists($river, $rivers)) {
            $rivers[$river] = "";
        }

        $rivers[$river] .= sprintf(
            "<tr><td style='background: %s;'>&nbsp;&nbsp;</td>" .
            "<td>%s</td>" .
                "<th>%s<br />" .
                "<a href=\"/plotting/auto/?q=160&amp;station=%s\"><i class=\"fa fa-signal\"></i> %s</a></th><td><a href='%s'>%s</a></td><td>%s</td>" .
                "<td>%s</td><td>%s</td><td><strong>Impact...</strong> %s</td></tr>",
            $sevcol[$row["severity"]],
            ($key == "W" ? "Flood Warning" : "Flood Watch"),
            $row["name"],
            $row["nwsli"],
            $row["nwsli"],
            $uri,
            $row["counties"],
            $row["stage_text"],
            $row["flood_text"],
            $row["forecast_text"],
            $row["impact_text"]
        );
    }
}
$content .= $ptitle;
$nselect = networkSelect("WFO", $wfo, array(), 'wfo');
$sselect = stateSelect($state);
$content .= <<<EOM
<p>This page produces a summary listing for National Weather Service Flood 
Forecast Points when the point is currently in a flood watch or warning state.
The IEM
processes the flood products and attempts to extract the important 
details regarding flood state, severity, forecasted stage and impact. By clicking
on the graph icon near the location identfier, you are taken to an IEM Autoplot
which shows forecasted stage and observations.</p>

<p>Data presented here was provided by this <a href="{$url}">JSON Web Service</a>.
Documentation on this webservice is
<a href="/api/1/docs#/default/service_nws_current_flood_warnings__fmt__get">here</a>.</p>


<h3>Three Ways to View Forecasts</h3>
<div class="row">
  <div class="col-md-4{$c1}">
    <h4>1. By NWS Forecast Office</h4>
<form method="GET" name="wfo">
{$nselect} <input type="submit" value="Select by WFO" class="btn btn-primary">
</form>
  </div>
  <div class="col-md-4{$c2}">
    <h4>2. By State</h4>
<form method='GET' name='state'>
{$sselect} <input type="submit" value="Select by State" class="btn btn-primary">
</form>
  </div>
  <div class="col-md-4{$c3}">
    <h4>3. Show all Available</h4>
    <a href="?all" class="btn btn-primary"><i class="fa fa-globe"></i> View All</a>

  </div>
</div>

<p>

<table class="table table-sm table-bordered">
<tr>
 <th>Key:</th>
 <td style="background: #ff0;">Near Flood Stage</td>
 <td style="background: #ff9900;">Minor Flooding</td>
 <td style="background: #f00;">Moderate Flooding</td>
 <td style="background: #f0f;">Major Flooding</td>
</tr>
</table>
EOM;

$content .= '<p><table class="table table-sm table-bordered">';
$rvs = array_keys($rivers);
asort($rvs);

foreach ($rvs as $idx => $key) {
    $content .=  "<tr><th colspan=\"8\" style='background: #eee; text-align: left;'>$key</th></tr>";
    $content .=  $rivers[$key];
}
if (sizeof($rvs) == 0) {
    $content .= "<tr><td colspan=\"8\">No Entries Found</td></tr>";
}

$content .=  "</table>";

$t->content = $content;
$t->render("full.phtml");
