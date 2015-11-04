<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 40);
 include("../../include/myview.php");
 include("../../include/mlib.php"); 
 include("../../include/network.php");
 include("../../include/forms.php");
 include("../../include/station.php");
 include("../../include/iemaccess.php");
 include("../../include/iemaccessob.php");
  
  $t = new MyView();
 
 $sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"] : "peak";
 $metar = isset($_GET["metar"]) ? $_GET['metar'] : "no";
 $sorder = isset($_GET["sorder"]) ? $_GET["sorder"] : "desc";
 $wfo = isset($_REQUEST["wfo"]) ? $_REQUEST["wfo"] : 'DMX';

 $t->refresh = "<meta http-equiv=\"refresh\" content=\"60;\">";
 $t->title = "Obs by NWS Forecast Office";

  $t->thispage = "current-sort";
  $nt = new NetworkTable("WFO");
 
$iem = new IEMAccess();
$asos = $iem->getWFO($wfo);


$vals = Array("tmpf" => "Air Temperature [F]", "dwpf" => "Dew Point Temp [F]",
  "sknt" => "Wind Speed [knots]", "drct" => "Wind Direction [deg]",
  "alti" => "Altimeter [mb]", "peak" => "Today's Wind Gust [knots]",
  "peak_ts" => "Time of Peak Gust", "relh" => "Relative Humidity",
  "feel" => "Feels Like [F]", "vsby" => "Visibility [miles]",
  "ts" => "Observation Time", "phour" => "Last Hour Rainfall [inch]",
  "min_tmpf" => "Today's Low Temperature",
  "max_tmpf" => "Today's High Temperature",
  "pday" => "Today Rainfall [inch]");

$t->current_network = "By NWS WFO"; 

$wselect = "<select name=\"wfo\">";
while( list($key, $value) = each($nt->table) ){
  $wselect .= "<option value=\"$key\" ";
  if ($wfo == $key) $wselect .= "SELECTED";
  $wselect .= ">[".$key."] ". $nt->table[$key]["name"] ."\n";
}
$wselect .= "</select>";

function aSortBySecondIndex($multiArray, $secondIndex) {
	global $sorder;
	while (list($firstIndex, $val) = each($multiArray)){
		if ($val == 0) continue;
		$indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];
	}
	if ($sorder == "asc")
		asort($indexMap);
	else
		arsort($indexMap);
	while (list($firstIndex, ) = each($indexMap))
	if (is_numeric($firstIndex))
		$sortedArray[] = $multiArray[$firstIndex];
	else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
	return $sortedArray;
}

$mydata = Array();
while (list($key, $iemob) = each($asos) ){
	$mydata[$key] = $iemob->db;
	$mydata[$key]["sped"] = $mydata[$key]["sknt"] * 1.15078;
	$mydata[$key]["relh"] = relh(f2c($mydata[$key]["tmpf"]), f2c($mydata[$key]["dwpf"]) );
	if ($mydata[$key]["relh"] < 5)
	{
		$mydata[$key]["relh"] = "M";
		$mydata[$key]["dewpf"] = "M";
		if ($sortcol == "feel" || $sortcol == "dwpf" || $sortcol == "relh") {
			$mydata[$key] = 0;
			continue;
		}
	}
	if ($mydata[$key]["tmpf"] < -60)
	{
		$mydata[$key]["tmpf"] = "M";
		if ($sortcol == "tmpf" || $sortcol == "feel" || $sortcol == "dwpf" || $sortcol == "relh") {
			$mydata[$key] = 0;
			continue;
		}
	}
	if ($mydata[$key]["alti"] < -60)
	{
		$mydata[$key]["alti"] = "M";
		if ($sortcol == "alti") {
			$mydata[$key] = 0;
			continue;
		}
	}
	if ($mydata[$key]["vsby"] < 0)
	{
		$mydata[$key]["vsby"] = "M";
		if ($sortcol == "vsby") {
			$mydata[$key] = 0;
			continue;
		}
	}


	$mydata[$key]["feel"] = feels_like($mydata[$key]["tmpf"],  $mydata[$key]["relh"], $mydata[$key]["sped"]);

	if ($mydata[$key]["max_gust"] > $mydata[$key]["max_sknt"]){
		$mydata[$key]["peak"] = $mydata[$key]["max_gust"];
		$mydata[$key]["peak_ts"] = strtotime(substr( $mydata[$key]["lmax_gust_ts"],0,16) );
	} else {
		$mydata[$key]["peak"] = $mydata[$key]["max_sknt"];
		$mydata[$key]["peak_ts"] = 0;
		if ($mydata[$key]["max_sknt_ts"] > 0)
		{
			$mydata[$key]["peak_ts"] = strtotime(substr( $mydata[$key]["lmax_sknt_ts"],0,16) );
		}
	}

}

$table = "";
$finalA = Array();
$finalA = aSortBySecondIndex($mydata, $sortcol);
$now = time();
$i = 0;
while (list ($key, $val) = each ($finalA))  {
	$i++;

	$parts = $finalA[$key];

	$table .= "<tr";
	if ($i % 2 == 0)  $table .= " bgcolor='#eeeeee'";
	$table .= "><td><input type=\"checkbox\" name=\"st[]\" value=\"".$key."\"></td>";

	$tdiff = $now - $parts["ts"];
	$moreinfo = sprintf("/sites/site.php?station=%s&network=%s", $key, $parts["network"]);
	$table .= "<td>". $parts["sname"] . " (<a href=\"$moreinfo\">". $key ."</a>,". $parts["network"] .")</td>";
	$table .= "<td ";
	if ($tdiff > 10000){
		$fmt = "%d %b %I:%M %p";
		$table .= 'bgcolor="red"';
	} else if ($tdiff > 7200){
		$fmt = "%I:%M %p";
		$table .= 'bgcolor="orange"';
	} else if ($tdiff > 3600){
		$fmt = "%I:%M %p";
		$table .= 'bgcolor="green"';
	} else {
		$fmt = "%I:%M %p";
	}

	$table .= ">". strftime($fmt, $asos[$key]->lts) ."</td>
     <td align='center'>". round($parts["tmpf"],0) ."(<font color=\"#ff0000\">". round($parts["max_tmpf"],0) ."</font>/<font color=\"#0000ff\">". round($parts["min_tmpf"],0) ."</font>)</td>
     <td>". round($parts["dwpf"],0) ."</td>
     <td>". round($parts["feel"],0) ."</td>
	    <td>". $parts["relh"] ."</td>
	    <td>". $parts["alti"] ."</td>
	    <td>". $parts["vsby"] ."</td>
             <td>". round($parts["sknt"],0) ;
	if (strlen($parts["gust"] != 0)){
		$table .= "G". round($parts["gust"],0);
	} $table .= "</td>";
	$table .= "<td>". $parts["drct"] ."</td>
	    <td>". round($parts["peak"],0) ." @ ". strftime("%I:%M %p", $parts["peak_ts"]) ."</td>
            <td>". $parts["phour"] ."</td>
            <td>". $parts["pday"] ."</td>
	    </tr>\n";
	if ($metar == "yes") {
		$table .= "<tr";
		if ($i % 2 == 0)  $table .= " bgcolor='#eeeeee'";
		$table .= ">";
		$table .= "<td colspan=14 align=\"CENTER\">
             <font color=\"brown\">". $parts["raw"] ."</font></td>
             </tr>\n";
	}
}
$uri = "obs.php?wfo=$wfo&metar=$metar&sorder=$sorder&sortcol=";

$ar = Array("no"=> "No", "yes"=> "Yes");
$mselect = make_select("metar", $metar, $ar);

$ar = Array("asc" => "Ascending", "desc" => "Descending");
$sselect = make_select("sorder", $sorder, $ar);

$t->content = <<<EOF
<p>
<form method="GET" action="obs.php" name="work">
<input type="hidden" value="{$sortcol}" name="sortcol">
<table class="table table-condensed">
<tr>
 <th>Select WFO: {$wselect}</td>
  <th>View Options:</th>
  <td>Include METARS: {$mselect}
</td>
<td>Sort Order: {$sselect}</td>
<td><input type="submit" value="Go!"></form></td>
</tr></table>

<p>Sorted by column <b>{$vals[$sortcol]}</b>. 
Timestamps displayed are the local time for the sensor.

<form method="GET" action="/my/current.phtml">

<table style="width: 100%; font-size: 10pt;" cellspacing=0 cellpadding=1 border=1>
<thead>
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
?>
