<?php
/* Fails when no polygon warning was present with the warning
   ex) CAR.SV.9.2007
*/
if (! isset($sts) ) die(); /* Avoid direct calls.... */

if (substr($_SERVER["REMOTE_ADDR"],0,6) == "66.249") die();

function printLSR($lsr)
{
  $lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg",
  "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout", "M" => "Marine Tstm Wnd",
"2" => "Dust Storm");
  $background = "#0f0";
  if ($lsr["warned"] == False) $background = "#f00";
  if ($lsr["leadtime"] == "NA") { $background = "#eee"; $leadtime = "NA"; }
  else {$leadtime = $lsr["leadtime"] ." minutes"; }
  if ($lsr["tdq"]) $background = "#aaa";
  if ($lsr["magnitude"] == 0) $lsr["magnitude"] = "";
  $uri = sprintf("../lsr/#%s/%s/%s", $lsr["wfo"], gmdate("YmdHi", $lsr["ts"]),
         gmdate("YmdHi", $lsr["ts"]) );
  return sprintf("<tr style=\"background: #eee;\"><td></td><td><a href=\"%s\" target=\"_new\">%s</a></td><td style=\"background: %s;\">%s</td><td>%s,%s</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td>%s</td><td>%s</td><td colspan=\"5\">%s</td></tr>", 
	$uri, gmdate("m/d/Y H:i", $lsr["ts"]), $background, $leadtime,
	$lsr["county"], $lsr["state"], $uri, $lsr["city"],
	$lt[strval($lsr["type"])], $lsr["magnitude"], $lsr["remark"]);
}
function clean_area_verify($buffered, $parea){
	if ($buffered === null) return 'invalid warning geometry';
	return sprintf("%.0f%%", $buffered / $parea * 100.0);
}
function printWARN($cow, $warn)
{
  global $lsrbuffer;
  $ts = $warn["sts"] + 5*60;
  $uri = sprintf("/vtec/#%s-O-%s-K%s-%s-%s-%04d", date("Y", $ts), 
        $warn["status"], $warn["wfo"], $warn["phenomena"], 
        $warn["significance"], $warn["eventid"]);
  $background = "#0f0";
  if ($warn["verify"] == False){ $background = "#f00"; }
  $bratio = "0";
  if ($warn["perimeter"] > 0){
  	$bratio = $warn["sharedborder"] / $warn["perimeter"] * 100.0;
  }
  $windhail = "";
  if ($warn["windtag"] != null){
  	$windhail = sprintf("<br />H: %s\"<br />W: %s", $warn["hailtag"], $warn["windtag"]);
  }

  $s = sprintf("<tr><td style=\"background: %s;\"><a href=\"%s\">%s.%s</a>%s</td>
  		<td>%s</td><td>%s</td>
  		<td colspan=\"2\"><a href=\"%s\" target=\"_new\">%s</a></td>
  		<td><a href=\"%s\">%s</a></td><td>%.0f sq km</td>
  		<td>%.0f sq km</td><td>%.0f %%</td>
  		<td>%.0f%% <a href=\"/GIS/radmap.php?layers[]=legend&layers[]=ci&layers[]=cbw&layers[]=sbw&layers[]=uscounties&layers[]=bufferedlsr&vtec=%s.K%s.%s.%s.%04d&lsrbuffer=%s\">Visual</a></td>
  		<td>%s</td><td>%s</td></tr>\n", 
    $background, $uri, $warn["phenomena"], $warn["eventid"], $windhail,
    gmdate("m/d/Y H:i", $warn["sts"]), gmdate("m/d/Y H:i", $warn["expire"]), 
    $uri, implode(", ", $warn["ugcname"]), $uri, $warn["status"], $warn["parea"], 
    $warn["carea"], ($warn["carea"] - $warn["parea"])/ $warn["carea"]  * 100,
    $bratio,
    date("Y", $ts), $warn["wfo"], $warn["phenomena"], $warn["significance"],
    $warn["eventid"], $lsrbuffer,
    clean_area_verify($warn["buffered"], $warn["parea"]), $warn["fcster"]);

  reset($warn["lsrs"]);
  if (sizeof($warn["lsrs"]) == 0 && $warn["verify"]){
  	$s .= "<tr><td></td><td colspan=\"10\">The warning above had one or more local
  			storm reports that were within previously issued warnings and are
  			not double counted here.  Thus the warning appears as verified,
  			but no local storm reports are shown. Future code improvements may 
  			be added to the Cow to better account for these.</td></tr>";
  }
  
  while ( list($k,$lsr) = each($warn["lsrs"])){ 
	$s .= printLSR($cow->lsrs[$lsr]); 
  }
  return $s;
}

include_once "../../include/cow.php";
$cow = new Cow( iemdb("postgis") );
// Allow for four char WFO
$usewfo = (strlen($wfo) == 4) ? substr($wfo, 1, 3): $wfo;
$cow->setLimitWFO( Array($usewfo) );
$cow->setLimitTime( $sts, $ets );
$cow->setHailSize( $hail );
$cow->setWind( $wind );
$cow->setLimitType( $wtype );
$cow->setLimitLSRType( $ltype );
$cow->setLSRBuffer( $lsrbuffer );
$cow->setWarningBuffer($warnbuffer);
$cow->setForecaster($fcster);
if (isset($useWindHailTag) && $useWindHailTag == 'Y'){
	$cow->useWindHailTag = true;
}
if (isset($limitwarns) && $limitwarns == 'Y'){
	$cow->limitwarns = true;
}
$cow->milk();

$charturl = sprintf("chart.php?aw=%s&ae=%s&b=%s&c=%s&d=%s",
            $cow->computeWarningsVerified(), $cow->computeWarnedEvents(),
            $cow->computeUnwarnedEvents(), $cow->computeWarningsUnverified(),
            "NA");

if (sizeof($ltype) == 0){
	$content .= "<div class='warning'>You did not select any of the Local Storm 
	Report types above, so none are listed below...<br /><br /></div>";
}
if (sizeof($wtype) == 0){
	$content .= "<div class='warning'>You did not select any of the Warning 
	types above, so none are listed below...<br /><br /></div>";
}

$dstat = date("m/d/Y H:i", $sts);
$dstat1 = date("m/d/Y H:i", $ets);


$aw = sprintf("%s", $cow->computeWarningsVerified());
$pv = sprintf("%.1f", $cow->computeWarningsVerifiedPercent());
$sr = sprintf("%.1f", $cow->computeSizeReduction());
$asz =  sprintf("%.0f", $cow->computeAverageSize());
$av = sprintf("%.0f", $cow->computeAreaVerify());
$ae = $cow->computeWarnedEvents();
$b = $cow->computeUnwarnedEvents();
$tdq = $cow->computeTDQEvents();

$wtable = "";
reset($cow->warnings);
$wsz = sizeof($cow->warnings);
while( list($k, $warn) = each($cow->warnings)){
	$wtable .= printWARN($cow, $warn);
}

$ltable = "";
reset($cow->lsrs);
$lsz = sizeof($cow->lsrs);
while ( list($k,$lsr) = each($cow->lsrs)){
	if ($lsr["warned"]) continue;

	$ltable .= printLSR($lsr);
}
$far = sprintf("%.2f", $cow->computeFAR());
$pod = sprintf("%.2f", $cow->computePOD());
$csi = sprintf("%.2f", $cow->computeCSI());

$aleadtime = sprintf("%.1f", $cow->computeAverageLeadTime());
$allleadtime = sprintf("%.1f", $cow->computeAllLeadTime());
$maxleadtime = sprintf("%.1f", $cow->computeMaxLeadTime());
$minleadtime = sprintf("%.1f", $cow->computeMinLeadTime());

$fwarning = "";
if ($fcster != ''){
	$fwarning = <<<EOF
<div class="alert alert-warning">
	<strong>This display is filtered for product signature: "{$fcster}".
	This means that the 'Unwarned Events' are not accurate as they may have
	verified by warnings signed by a different string.</strong></div>
EOF;
}

$content .= <<<EOF
<h3>Summary:</h3>
<b>Begin Date:</b> {$dstat} <b>End Date:</b> {$dstat1}
<br />* These numbers are not official and should be used for educational purposes only.
${fwarning}

<div class="row">
  <div class="col-sm-2">
  	<img src="cow.jpg" class="img img-responsive" /><br />
  	<img src="{$charturl}"  class="img img-responsive"/>
  </div>
	<div class="col-sm-5">
 <table class="table table-condensed">
 <tr><th>Listed Warnings:</th><th>{$wsz}</th></tr>
 <tr><th>Verified: (A<sub>w</sub>)</th><th>{$aw}</th></tr>
 <tr><th>% Verified</th><th>{$pv}%</th></tr>
 <tr><th>Storm Based Warning Size Reduction:</th><th>{$sr}%</th></tr>
 <tr><th>Avg SBW Size (sq km)</th><th>{$asz}</th></tr>
 <tr><th>Areal Verification %:</th><th>{$av}%</th></tr>
 <tr><th>Reports</th><th>{$lsz}</th></tr>
 <tr><th>Warned Events (A<sub>e</sub>)</th><th>{$ae}</th></tr>
 <tr><th>Unwarned Events (B)</th><th>{$b}</th></tr>
 <tr><th>Non TOR LSRs during TOR warning</th><th>{$tdq}</th></tr>
 </table>
	</div>
	<div class="col-sm-5">
 <table class="table table-condensed">
 <tr><th>FAR == C / (A<sub>w</sub>+C)</th><th>{$far}</th></tr>
 <tr><th>POD == A<sub>e</sub> / (A<sub>e</sub> + B)</th><th>{$pod}</th></tr>
 <tr><th>CSI == ((POD)<sup>-1</sup> + (1-FAR)<sup>-1</sup> - 1)<sup>-1</sup></th><th>{$csi}</th></tr>
 <tr><th>Avg Lead Time for 1rst Event</th><th>{$aleadtime} min</th></tr>
 <tr><th>Avg Lead Time for all Events</th><th>{$allleadtime} min</th></tr>
 <tr><th>Max Lead Time</th><th>{$maxleadtime} min</th></tr>
 <tr><th>Min Lead Time</th><th>{$minleadtime} min</th></tr>
 </table>
	</div>
</div>



<h3 class="heading">Warnings Issued & Verifying LSRs:</h3>
<strong>Column Headings:</strong> 
<i>Issued:</i> UTC timestamp of when the product was issued, 
<i>Expired:</i> UTC timestamp of when the product expired,
<i>Final Status:</i> VTEC action of the last statement issued for the product,
<i>SBW Area:</i> Size of the storm based warning in square km,
<i>County Area:</i> Total size of the counties included in the product in square km,
<i>Size % (C-P)/C:</i> Size reduction gained by the storm based warning,
<i>Perimeter Ratio:</i> Estimated percentage of the storm based warning polygon border that was influenced by political boundaries (0% is ideal).
<i>Areal Verification %:</i> Percentage of the polygon warning that received a verifying report (report is buffered {$lsrbuffer} km).
<br />The second line is for details on any local storm reports.
<br />
<table cellspacing="0" cellpadding="2" border="1">
<tr>
	<td></td>
	<th>Issued:</th>
	<th>Expired:</th>
	<th colspan="2">County:</th>
	<th>Final Status:</th>
	<th>SBW Area: (P)</th>
	<th>County Area: (C)</th>
	<th>Size %<br /> (C-P)/C:</th>
	<th>Perimeter Ratio:</th>
	<th>Areal Verif. %:</th>
	<th>Signature</th>
</tr>
<tr bgcolor="#eee">
	<th>lsr</th>
	<th>Valid</th>
	<th>Lead Time:</th>
	<th>County</th>
	<th>City</th>
	<th>Type</th>
	<th>Magnitude</th>
	<th colspan="5">Remarks</th>
</tr>
{$wtable}
</table>

<h3>Storm Reports without warning:</h3> 
<table class="table table-bordered table-condensed">
<tr>
	<th>lsr</th>
	<th>Valid</th>
	<th>Lead Time:</th>
	<th>County</th>
	<th>City</th>
	<th>Type</th>
	<th>Magnitude</th>
	<th>Remark</th>
</tr>
{$ltable}
</table>
EOF;
