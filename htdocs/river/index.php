<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 71);
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
require_once "../../include/myview.php";

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
 $nwsli_limiter = "and hvtec_nwsli IN ('FLTI2', 'CMMI4', 'LECI4', 'RCKI2', 'ILNI2', 
 'MUSI4', 'NBOI2', 'KHBI2', 'DEWI4', 'CNEI4', 'CJTI4', 'WAPI4','LNTI4', 'CMOI2', 
 'JOSI2', 'MLII2','GENI2')";
 $content .= "<style>
body {
  background: #fff;
  font-size: smaller;
}
</style>";
}

$thisyear = date("Y");
$statelimiter = "";
$wfolimiter = "";
$c1 = "";
$c2 = "";
$c3 = "";
if (isset($_REQUEST["state"])){
    $c2 = " well";
    $statelimiter = sprintf(" and substr(ugc, 1, 2) = '%s' ", $state);
    $ptitle = "<h3>River Forecast Point Monitor by State</h3>";
} else if (isset($_REQUEST["all"])){
    $c3 = " well";
    $ptitle = "<h3>River Forecast Point Monitor (view all)</h3>";
} else {
    $c1 = " well";
    $wfolimiter = sprintf(" and wfo = '%s' ", $wfo);
    $ptitle = "<h3>River Forecast Point Monitor by NWS WFO</h3>";
}

$sql = <<<EOM
WITH warns as (
    SELECT w.hvtec_nwsli, w.ugc, w.gid, w.eventid, w.phenomena, w.wfo,
    h.name, h.river_name
    from warnings_{$thisyear} w JOIN hvtec_nwsli h
        on (w.hvtec_nwsli = h.nwsli) WHERE
    status NOT IN ('EXP','CAN') and phenomena = 'FL' and
    significance = 'W' and  expire > now() $nwsli_limiter $statelimiter
    $wfolimiter
), names as (
    SELECT hvtec_nwsli, sumtxt(u.name || ', ') as counties
    from warns w, ugcs u WHERE w.gid = u.gid GROUP by hvtec_nwsli
), agg as (
    SELECT w.*, n.counties
    from warns w JOIN names n on (w.hvtec_nwsli = n.hvtec_nwsli)
)
SELECT r.*, a.* from riverpro r JOIN agg a on (r.nwsli = a.hvtec_nwsli)
ORDER by a.name ASC
EOM;
$rs = pg_query($postgis, $sql);

$rivers = Array();
$used = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
    if (in_array($row["nwsli"], $used)) {
        continue;
    }
    $used[] = $row["nwsli"];
  $river = $row["river_name"];
  $uri = sprintf("/vtec/#%s-O-%s-K%s-%s-%s-%04d", date("Y"),
        "NEW", $row["wfo"], $row["phenomena"],
        "W", $row["eventid"]);


  @$rivers[$river] .= sprintf("<tr><td style='background: %s;'>&nbsp;&nbsp;</td>".
      "<th>%s<br />".
      "<a href=\"/plotting/auto/?q=160&amp;station=%s\"><i class=\"fa fa-signal\"></i> %s</a></th><td><a href='%s'>%s</a></td><td>%s</td>".
      "<td>%s</td><td>%s</td><td><strong>Impact...</strong> %s</td></tr>",
      $sevcol[$row["severity"]], $row["name"], 
      $row["nwsli"], $row["nwsli"], $uri, $row["counties"], $row["stage_text"],
      $row["flood_text"], $row["forecast_text"], $row["impact_text"]);
}
$content .= $ptitle;
$nselect = networkSelect("WFO", $wfo, Array(), 'wfo');
$sselect = stateSelect($state);
$content .= <<<EOF
<p>This page produces a summary listing for National Weather Service Flood 
Forecast Points when the point is currently in a flood warning state.  The IEM
processes the flood warning products and attempts to extract the important 
details regarding flood state, severity, forecasted stage and impact. By clicking
on the graph icon near the location identfier, you are taken to an IEM Autoplot
which shows forecasted stage and observations.</p>

<h3>Three Ways to View Forecasts</h3>
<div class="row">
  <div class="col-md-4{$c1}">
    <h4>1. By NWS Forecast Office</h4>
<form method="GET" name="wfo">
{$nselect} <input type="submit" value="Select by WFO">
</form>
  </div>
  <div class="col-md-4{$c2}">
    <h4>2. By State</h4>
<form method='GET' name='state'>
{$sselect} <input type="submit" value="Select by State">
</form>
  </div>
  <div class="col-md-4{$c3}">
    <h4>3. Show all Available</h4>
    <a href="?all" class="btn btn-primary"><i class="fa fa-globe"></i> View All</a>

  </div>
</div>

<p>

<table class="table table-condensed table-bordered">
<tr>
 <th>&nbsp; &nbsp;</th>
 <th>Key:</th>
 <td style="background: #ff0;">Near Flood Stage</td>
 <td style="background: #ff9900;">Minor Flooding</td>
 <td style="background: #f00;">Moderate Flooding</td>
 <td style="background: #f0f;">Major Flooding</td>
</tr></table>
EOF;

$content .= '<p><table class="table table-condensed table-bordered">';
$rvs = array_keys($rivers);
asort($rvs);

foreach($rvs as $idx => $key)
{
  $content .=  "<tr><th colspan=\"7\" style='background: #eee; text-align: left;'>$key</th></tr>";
  $content .=  $rivers[$key];

}
if (sizeof($rvs) == 0){
	$content .= "<tr><td colspan=\"7\">No Entries Found</td></tr>";
}

$content .=  "</table>";

$t->content = $content;
$t->render("full.phtml");
?>
