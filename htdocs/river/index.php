<?php
include("../../config/settings.inc.php");
define("IEM_APPID", 71);
include("../../include/database.inc.php");
include("../../include/forms.php");
include("../../include/imagemaps.php");
include("../../include/myview.php");

$t = new MyView();
$t->thispage = "severe-river";
$t->title = "River Forecast Point Monitor";
$content = "";

$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3): "DMX";
$state = isset($_GET["state"]) ? substr($_GET["state"],0,3): "IA";

$postgis = iemdb("postgis");
$sevcol = Array(
 "N" =>"#0f0",
 "0" =>"#ff0",
 "1" =>"#ff9900",
 "2" =>"#f00",
 "3" =>"#f0f",
 "U" =>"#fff");

$nwsli_limiter = "";
if (isset($_GET["dvn"])){
 $nwsli_limiter = "and r.nwsli IN ('FLTI2', 'CMMI4', 'LECI4', 'RCKI2', 'ILNI2', 
 'MUSI4', 'NBOI2', 'KHBI2', 'DEWI4', 'CNEI4', 'CJTI4', 'WAPI4','LNTI4', 'CMOI2', 
 'JOSI2', 'MLII2','GENI2')";
 $content .= "<style>
#iem-header {
  display: none;
  visibility: hidden;
}
#iem-footer {
  display: none;
  visibility: hidden;
}
body {
  background: #fff;
  font-size: smaller;
}
</style>";
}

if (isset($_REQUEST["state"])){
 $rs = pg_prepare($postgis, "SELECT", "select h.name, h.river_name, h.nwsli, 
 foo.wfo, foo.eventid, foo.phenomena, r.severity, r.stage_text, 
 r.flood_text, r.forecast_text, sumtxt(c.name || ', ') as counties from hvtec_nwsli h, 
   riverpro r, nws_ugc c, 
  (select distinct hvtec_nwsli, ugc, eventid, phenomena, wfo from warnings_". date("Y") ." WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W' and hvtec_nwsli IN (select nwsli from hvtec_nwsli WHERE state = $1 and
   		 expire > now())) as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli $nwsli_limiter
   and c.ugc = foo.ugc GROUP by h.river_name, h.name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity,
   r.stage_text, r.flood_text, r.forecast_text");
 $rs = pg_execute($postgis, "SELECT", Array($state));
 $ptitle = "<h3>River Forecast Point Monitor by State</h3>";
} else if (isset($_REQUEST["all"])){
 $rs = pg_prepare($postgis, "SELECT", "select h.name, h.river_name, h.nwsli, 
 foo.wfo, foo.eventid, foo.phenomena, r.severity, r.stage_text, 
 r.flood_text, r.forecast_text, sumtxt(c.name || ', ') as counties from hvtec_nwsli h, 
   riverpro r, nws_ugc c, 
  (select distinct hvtec_nwsli, ugc, eventid, phenomena, wfo from warnings_". date("Y") ." WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W' and  expire > now()) as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli 
   and c.ugc = foo.ugc GROUP by h.river_name, h.name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity,
   r.stage_text, r.flood_text, r.forecast_text");
 $rs = pg_execute($postgis, "SELECT", Array());
 $ptitle = "<h3>River Forecast Point Monitor (view all)</h3>";
} else {
 $rs = pg_prepare($postgis, "SELECT", "select h.name, h.river_name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity, r.stage_text, r.flood_text, r.forecast_text, 
   sumtxt(c.name || ', ') as counties
   from hvtec_nwsli h, riverpro r, nws_ugc c,
  (select distinct hvtec_nwsli, ugc, eventid, phenomena, wfo from warnings_". date("Y") ." WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W' and wfo = $1 and expire > now()) as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli $nwsli_limiter
   and c.ugc = foo.ugc GROUP by h.river_name, h.name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity,
   r.stage_text, r.flood_text, r.forecast_text");
 $rs = pg_execute($postgis, "SELECT", Array($wfo));
 $ptitle = "<h3>River Forecast Point Monitor by NWS WFO</h3>";
}


$rivers = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $river = $row["river_name"];
  $uri = sprintf("/vtec/#%s-O-%s-K%s-%s-%s-%04d", date("Y"),
        "NEW", $row["wfo"], $row["phenomena"],
        "W", $row["eventid"]);


  @$rivers[$river] .= sprintf("<tr><th style='background: %s;'>%s<br />%s</th><td><a href='%s'>%s</a></td></th><td>%s</td><td>%s</td><td>%s</td></tr>",$sevcol[$row["severity"]], $row["name"], 
   $row["nwsli"], $uri, $row["counties"], $row["stage_text"], $row["flood_text"], 
   $row["forecast_text"]);
}
$content .= $ptitle;
$content .= <<<EOF
<p>This page produces a summary listing for National Weather Service Flood 
Forecast Points when the point is currently in a flood warning state.  The IEM
processes the flood warning products and attempts to extract the important 
details regarding flood state, severity, and forecasted stage.</p>
<a href="?all">View All</a>
<p><form method="GET" name="wfo">
EOF;
$content .= 'Select by NWS Forecast Office:'. networkSelect("WFO", $wfo, Array(), 'wfo');
$content .= "<input type='submit' value='Select by WFO'>";
$content .= "</form>";
$sselect = stateSelect($state);
$content .= <<<EOF
<p><form method='GET' name='state'>
Select by State: 
{$sselect}
<input type='submit' value="Select by State">
</form>

<table border='1' cellpadding='2' cellspacing='0' style="margin: 5px;">
<tr>
 <th>Key:</th>
 <td style="background: #ff0;">Near Flood Stage</td>
 <td style="background: #ff9900;">Minor Flooding</td>
 <td style="background: #f00;">Moderate Flooding</td>
 <td style="background: #f0f;">Major Flooding</td>
</tr></table>
EOF;

$content .= "<p><table border='1' cellpadding='2' cellspacing='0'>";
$rvs = array_keys($rivers);
asort($rvs);

while (list($idx, $key) = each($rvs))
{
  $content .=  "<tr><th colspan='5' style='background: #eee; text-align: left;'>$key</th></tr>";
  $content .=  $rivers[$key];

}
if (sizeof($rvs) == 0){
	$content .= "<tr><td colspan='5'>No Entries Found</td></tr>";
}

$content .=  "</table>";

$t->content = $content;
$t->render("single.phtml");
?>
