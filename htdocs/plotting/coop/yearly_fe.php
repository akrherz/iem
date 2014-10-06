<?php 
include("../../../config/settings.inc.php");
include("../../../include/network.php");
include_once "../../../include/forms.php";
include_once "../../../include/myview.php";
$t = new MyView();
$t->title = "COOP Climate Plots";

$station1 = isset($_GET["station1"]) ? $_GET["station1"] : "";
$station2 = isset($_GET["station2"]) ? $_GET["station2"] : "";
$mode = isset($_GET["mode"]) ? $_GET["mode"]: "";
$season = isset($_GET["season"]) ? $_GET["season"]: "";

$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$s1 = "";
for(reset($cities); $key = key($cities); next($cities))
{
	$s1 .= "<option value=\"" . $cities[$key]["id"] ."\"";
	if ($cities[$key]["id"] == $station1) $s1 .= " SELECTED ";

	$s1 .= ">" . $cities[$key]["name"] . "\n";
}

$s2 = "";
for(reset($cities); $key = key($cities); next($cities))
{
	$s2 .= "<option value=\"" . $cities[$key]["id"] ."\"";
	if ($cities[$key]["id"] == $station2) $s2 .= " SELECTED ";

	$s2 .= ">" . $cities[$key]["name"] . "\n";
}

$ar = Array("o" => "One Station", "c" => "Compare Two");
$modeselect = make_select("mode", $mode, $ar);

$ar = Array("all" => "All",
		"winter" => "Winter (DJF)",
		"spring" => "Spring (NAM)",
		"summer" => "Summer (JJA)",
		"fall" => "Fall (SON)");
$seasonselect = make_select("season", $season, $ar);

if ($mode == "c"){
	$im = "<img src=\"yearly_diff.php?station1=".$station1."&station2=".$station2."&season=".$season."\">\n";

}else if (strlen($station1) > 0 ){
	$im = "<img src=\"yearly.php?station=". $station1 ."&season=".$season."\">\n";
}else{
	$im = "<p>Please make plot selections above.\n";
}


$t->content = <<<EOF
<ol class="breadcrumb">
<li><a href="http://mesonet.agron.iastate.edu/">IEM</a></li>
<li><a href="/climate/">Climatology</a></li>
<li class="active">COOP Yearly Averages</li>
</ol>

<p>Using the historical COOP data archive, this application plots yearly
temperature averages.  You can plot averages for a single station or compare
two stations side-by-side.</p>



     <b>Make Plot Selections:</b>
  

<form method="GET" action="yearly_fe.php">

<table>
<tr>
  <th class="subtitle">Station 1</th>
  <th class="subtitle">Station 2</th>
  <th class="subtitle">Plot Mode</th>
  <th class="subtitle">Seasons?</th>
  <td></td>
</tr>

<tr>
<td>
<SELECT name="station1">{$s1}</SELECT>
</td>
<td>
<SELECT name="station2">{$s2}</SELECT>
</td>
<td>{$modeselect}
</td>

<td>
{$seasonselect}
</td>


<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

		{$im}

EOF;
$t->render('single.phtml');
?>
