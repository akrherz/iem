<?php
/* Fails when no polygon warning was present with the warning
   ex) CAR.SV.9.2007
*/
if (! isset($sts) ) die(); /* Avoid direct calls.... */

function printLSR($lsr)
{
  $lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg", "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout", "M" => "Marine Tstm Wnd");
  $background = "#0f0";
  if ($lsr["warned"] == False) $background = "#f00";
  if ($lsr["leadtime"] == "NA") { $background = "#eee"; $leadtime = "NA"; }
  else {$leadtime = $lsr["leadtime"] ." minutes"; }
  if ($lsr["tdq"]) $background = "#aaa";
  if ($lsr["magnitude"] == 0) $lsr["magnitude"] = "";
  $uri = sprintf("../lsr/#%s/%s/%s", $lsr["wfo"], gmdate("YmdHi", $lsr["ts"]),
         gmdate("YmdHi", $lsr["ts"]) );
  return sprintf("<tr style=\"background: #eee;\"><td></td><td><a href=\"%s\" target=\"_new\">%s</a></td><td style=\"background: %s;\">%s</td><td>%s,%s</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td>%s</td><td>%s</td><td colspan=\"4\">%s</td></tr>", 
    $uri, gmdate("m/d/Y H:i", $lsr["ts"]), $background, $leadtime, $lsr["county"], $lsr["state"], $uri, $lsr["city"], $lt[$lsr["type"]], $lsr["magnitude"], $lsr["remark"]);
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
  $counties = Array();
  $carea = 0;
  reset($warn["ugc"]);
  while ( list($k,$v) = each($warn["ugc"])){
    $counties[] = $cow->ugcCache[$v]["name"];
    $carea += $cow->ugcCache[$v]["area"];
  }

  $s = sprintf("<tr><td style=\"background: %s;\"><a href=\"%s\">%s.%s</a></td><td>%s</td><td>%s</td><td colspan=\"2\"><a href=\"%s\" target=\"_new\">%s</a></td><td><a href=\"%s\">%s</a></td><td>%.0f sq km</td><td>%.0f sq km</td><td>%.0f %%</td><td>%.0f%% <a href=\"../GIS/radmap.php?layers[]=legend&layers[]=ci&layers[]=cbw&layers[]=sbw&layers[]=uscounties&layers[]=bufferedlsr&vtec=%s.K%s.%s.%s.%04d&lsrbuffer=%s\">Visual</a></td><td>%.0f%%</td></tr>\n", 
    $background, $uri, $warn["phenomena"], $warn["eventid"],
    gmdate("m/d/Y H:i", $warn["sts"]), gmdate("m/d/Y H:i", $warn["ets"]), 
    $uri, implode(", ",$counties), $uri, $warn["status"], $warn["area"], 
    $carea, ($carea - $warn["parea"])/ $carea  * 100,
    $warn["sharedborder"] / $warn["perimeter"] * 100.0,
    date("Y", $ts), $warn["wfo"], $warn["phenomena"], $warn["significance"],
    $warn["eventid"], $lsrbuffer,
    $warn["buffered"] / $warn["area"] * 100.0);

  reset($warn["lsrs"]);
  while ( list($k,$lsr) = each($warn["lsrs"])){ $s .= printLSR($cow->lsrs[$lsr]); }
  return $s;
}

include("$rootpath/include/cow.php");
$cow = new Cow( iemdb("postgis") );
$cow->setLimitWFO( Array($wfo) );
$cow->setLimitTime( $sts, $ets );
$cow->setHailSize( $hail );
$cow->setLimitType( $wtype );
$cow->setLimitLSRType( $ltype );
$cow->setLSRBuffer( $lsrbuffer );
$cow->milk();

$charturl = sprintf("chart.php?aw=%s&ae=%s&b=%s&c=%s&d=%s",
            $cow->computeWarningsVerified(), $cow->computeWarnedEvents(),
            $cow->computeUnwarnedEvents(), $cow->computeWarningsUnverified(),
            "NA");

?>
<h3 class="heading">Summary:</h3>
<?php echo "<b>Begin Date:</b> ". date("m/d/Y H:i", $sts) ." <b>End Date:</b> ". date("m/d/Y H:i", $ets); ?>
<br />* These numbers are not official and should be used for educational purposes only.

<table cellspacing="1" cellpadding="2" border="1">
<tr>
<td>
<?php echo sprintf("<img src=\"%s\" align=\"left\">", $charturl, "NA"); ?>
</td>
<td>
 <table cellspacing="0" cellpadding="3" border="1">
 <tr><th>Listed Warnings:</th><th><?php echo sizeof($cow->warnings) ?></th></tr>
 <tr><th>Verified: (A<sub>w</sub>)</th><th><?php echo sprintf("%s", $cow->computeWarningsVerified()); ?></th></tr>
 <tr><th>% Verified</th><th><?php echo sprintf("%.1f", $cow->computeWarningsVerifiedPercent()); ?> %</th></tr>
 <tr><th>Storm Based Warning Size Reduction:</th>
<th><?php echo sprintf("%.1f", $cow->computeSizeReduction()); ?> %</th></tr>
 <tr><th>Avg SBW Size (sq km)</th><th><?php echo sprintf("%.0f", $cow->computeAverageSize()); ?></th></tr>
 <tr><th>Warned Area Verified</th><th><?php echo sprintf("%.0f", $cow->computeAreaVerify()); ?> %</th></tr>
 </table>
</td>
<td>
 <table cellspacing="1" cellpadding="2" border="1">
 <tr><th>Reports</th><th><?php echo sizeof($cow->lsrs) ?></th></tr>
 <tr><th>Warned Events (A<sub>e</sub>)</th><th><?php echo $cow->computeWarnedEvents(); ?></th></tr>
 <tr><th>Unwarned Events (B)</th><th><?php echo $cow->computeUnwarnedEvents(); ?></th></tr>
 <tr><th>Non TOR LSRs during TOR warning</th><th><?php echo $cow->computeTDQEvents(); ?></th></tr>
 </table>
</td>
<td><img src="cow.jpg"></td>
</tr>
<tr>
<td colspan="4">
 <table cellspacing="1" cellpadding="2" border="1">
 <tr>
 <th>FAR == C / (A<sub>w</sub>+C) = <span style="color: #f00;"><?php echo sprintf("%.2f", $cow->computeFAR()); ?></span></th>
 <th>POD == A<sub>e</sub> / (A<sub>e</sub> + B) = <span style="color: #f00;"><?php echo sprintf("%.2f", $cow->computePOD()); ?></span></th>
 <th>CSI == ((POD)<sup>-1</sup> + (1-FAR)<sup>-1</sup> - 1)<sup>-1</sup> = <span style="color: #f00;"><?php echo sprintf("%.2f", $cow->computeCSI()); ?></span></th>
 </tr>
 </table>
</td>
</tr>
<tr>
<td colspan="3">
 <table cellspacing="1" cellpadding="2" border="1">
 <tr>
 <th>Avg Lead Time for 1rst Event</th><th><?php echo sprintf("%.1f", $cow->computeAverageLeadTime()); ?></th>
 <th>Avg Lead Time for all Events</th><th><?php echo sprintf("%.1f", $cow->computeAllLeadTime()); ?></th>
 <th>Max Lead Time</th><th><?php echo sprintf("%.1f", $cow->computeMaxLeadTime()); ?></th>
 <th>Min Lead Time</th><th><?php echo sprintf("%.1f", $cow->computeMinLeadTime()); ?></th>
 </tr>
 </table>
</td></tr>
</table>
<h3 class="heading">Warnings Issued & Verifying LSRs:</h3>
<strong>Column Headings:</strong> 
<i>Issued:</i> GMT timestamp of when the product was issued, 
<i>Expired:</i> GMT timestamp of when the product expired,
<i>Final Status:</i> VTEC action of the last statement issued for the product,
<i>SBW Area:</i> Size of the storm based warning in square km,
<i>County Area:</i> Total size of the counties included in the product in square km,
<i>Size % (C-P)/C:</i> Size reduction gained by the storm based warning,
<i>Perimeter Ratio:</i> Estimated percentage of the storm based warning polygon border that was influenced by political boundaries (0% is ideal).
<i>Verif Area %:</i> Percentage of the polygon warning that received a verifying report (report is buffered <?php echo $lsrbuffer; ?> km).
<br />The second line is for details on any local storm reports.
<br />
<table cellspacing="0" cellpadding="2" border="1">
<tr><td></td><th>Issued:</th><th>Expired:</th><th colspan="2">County:</th><th>Final Status:</th><th>SBW Area: (P)</th><th>County Area: (C)</th><th>Size %<br /> (C-P)/C:</th><th>Perimeter Ratio:</th><th>Verif Area %:</th></tr>
<tr bgcolor="#eee"><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th><th colspan="4">Remarks</th></tr>
<?php
reset($cow->warnings);
while( list($k, $warn) = each($cow->warnings)){
  echo printWARN($cow, $warn);
}
?>
</table>

<h3 class="heading">Storm Reports without warning:</h3> 
<table cellspacing="1" cellpadding="2" border="1">
<tr><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th></tr>
<?php
reset($cow->lsrs);
while ( list($k,$lsr) = each($cow->lsrs)){
  if ($lsr["warned"]) continue;

  echo printLSR($lsr);
}
?>
</table>
