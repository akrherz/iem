<?php
/* Fails when no polygon warning was present with the warning
   ex) CAR.SV.9.2007
*/
if (! isset($sts) ) die(); /* Avoid direct calls.... */
$conn = iemdb("postgis");
pg_query($conn, "SET TIME ZONE 'GMT'");

$stsSQL = date("Y/m/d H:i", $sts);
$etsSQL = date("Y/m/d H:i", $ets);

$DEBUG = "";

function printLSR($lsr)
{
  $lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg", "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout", "M" => "Marine Tstm Wnd");
  $background = "#0f0";
  if ($lsr["warned"] == 0) $background = "#f00";
  if ($lsr["leadtime"] == "NA") { $background = "#eee"; $leadtime = "NA"; }
  else {$leadtime = $lsr["leadtime"] ." minutes"; }
  if ($lsr["tdq"] > 0) $background = "#aaa";
  if ($lsr["magnitude"] == 0) $lsr["magnitude"] = "";
  //if ($lsr["ts"] < 100000) print_r($lsr);
  $uri = sprintf("maplsr.phtml?lat0=%s&lon0=%s&ts=%s", $lsr["lat0"], $lsr["lon0"], gmdate("Y-m-d%20H:i", $lsr["ts"]));
  return sprintf("<tr style=\"background: #eee;\"><td>lsr</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td style=\"background: %s;\">%s</td><td>%s,%s</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td>%s</td><td>%s</td><td colspan=\"3\">%s</td></tr>", 
    $uri, gmdate("m/d/Y H:i", $lsr["ts"]), $background, $leadtime, $lsr["county"], $lsr["state"], $uri, $lsr["city"], $lt[$lsr["type"]], $lsr["magnitude"], $lsr["remark"]);
}
function printWARN($warn)
{
  $ts = $warn["sts"] + 5*60;
  $uri = sprintf("/vtec/%s-O-%s-K%s-%s-%s-%04d.html", date("Y", $ts), 
        $warn["status"], $warn["wfo"], $warn["phenomena"], 
        $warn["significance"], $warn["eventid"]);
  $background = "#0f0";
  if ($warn["verify"] == 0){ $background = "#f00"; }

  return sprintf("<tr><td style=\"background: %s;\"><a href=\"%s\">%s.%s</a></td><td>%s</td><td>%s</td><td colspan=\"2\"><a href=\"%s\" target=\"_new\">%s</a></td><td><a href=\"%s\">%s</a></td><td>%.0f km^2</td><td>%.0f km^2</td><td>%.0f %%</td><td>%.0f%%</td></tr>\n", 
    $background, $uri, $warn["phenomena"], $warn["eventid"],
    gmdate("m/d/Y H:i", $warn["sts"]), gmdate("m/d/Y H:i", $warn["ets"]), 
    $uri, $warn["counties"], $uri, $warn["status"], $warn["area"], 
    $warn["carea"], ($warn["carea"]-$warn["area"])/ $warn["carea"] * 100,
    $warn["sharedborder"] / $warn["perimeter"] * 100.0);

}

/* First, we need to go hunting for warnings of all types to build 
   up some arrays */
$warnings = Array();
$wtypeSQL = "";
reset($wtype);
while( list($k,$v) = each($wtype)){ $wtypeSQL .= sprintf("'%s',",$v); }
$wtypeSQL .= "'ZZ'"; /* Hack */
$sql = sprintf("select *, astext(geom) as tgeom from (SELECT distinct * from 
   (select *, area(transform(geom,2163)) / 1000000.0 as area,
    perimeter(transform(geom,2163)) as perimeter,
    xmax(geom) as lon0, ymax(geom) as lat0 from 
    warnings_%s WHERE wfo = '%s' and issue >= '%s' and expire < '%s' 
    and phenomena IN (%s) and significance != 'A' ORDER by issue ASC) as foo) as foo",
   date("Y", $sts), $wfo, $stsSQL, $etsSQL, $wtypeSQL);
$DEBUG .=  "<br />". $sql;
$rs = pg_query($conn, $sql);
$sum_parea = 0;
$sum_carea = 0;
for ($i=0;$row = @pg_fetch_array($rs,$i);$i++)
{
  $key = sprintf("%s-%s-%s", $row["wfo"], $row["phenomena"], $row["eventid"]);
  if ( ! isset($warnings[$key]) ){ 
    $warnings[$key] = Array("counties"=> "", "carea" => 0 );
  }
  $warnings[$key]["issue"] = $row["issue"];
  $warnings[$key]["expire"] = $row["expire"];
  $warnings[$key]["phenomena"] = $row["phenomena"];
  $warnings[$key]["wfo"] = $row["wfo"];
  $warnings[$key]["status"] = $row["status"];
  $warnings[$key]["significance"] = $row["significance"];
  $warnings[$key]["area"] = $row["area"];
  $warnings[$key]["lat0"] = $row["lat0"];
  $warnings[$key]["lon0"] = $row["lon0"];
  $warnings[$key]["sts"] = strtotime($row["issue"]);
  $warnings[$key]["ets"] = strtotime($row["expire"]);
  $warnings[$key]["eventid"] = $row["eventid"];
  $warnings[$key]["lead0"] = -1;
  if ($row["gtype"] == "P"){ 
    $sum_parea += $row["area"];
    $warnings[$key]["geom"] = $row["tgeom"]; 
    $warnings[$key]["gtype"] = $row["gtype"];
    $warnings[$key]["perimeter"] = $row["perimeter"];
    /* Now, lets compute the shared border! */
    $sql = sprintf("SELECT sum(sz) as s from (
     SELECT length(transform(a,2163)) as sz from (
        select 
           intersection(
      buffer(exteriorring(geometryn(multi(geomunion(n.geom)),1)),0.02),
      exteriorring(geometryn(multi(geomunion(w.geom)),1))
            )  as a
            from warnings_%s w, nws_ugc n WHERE gtype = 'P' 
            and w.wfo = '%s' and phenomena = '%s' and eventid = '%s' 
            and significance = '%s' and n.polygon_class = 'C'
            and st_overlaps(n.geom, w.geom) 
            and n.ugc IN (
                SELECT ugc from warnings_%s WHERE
                gtype = 'C' and wfo = '%s' 
          and phenomena = '%s' and eventid = '%s' and significance = '%s'
       )
         ) as foo
            WHERE not isempty(a) ) as foo
       ", date("Y", $sts), $wfo, $row["phenomena"],
            $row["eventid"], $row["significance"],
          date("Y", $sts), $wfo, $row["phenomena"],
            $row["eventid"], $row["significance"] );
    $DEBUG .= "<br />". $sql;
    $brs = pg_query($conn, $sql);
    if (pg_num_rows($brs) > 0) {
       $brow = pg_fetch_array($brs,0);
       $warnings[$key]["sharedborder"] = $brow["s"];
    }
  }
  $warnings[$key]["verify"] = 0;
  if ($row["gtype"] == "C")
  {
     $sql = sprintf("SELECT *, area(transform(geom,2163)) / 1000000.0 as area 
                     from nws_ugc WHERE ugc = '%s'", $row["ugc"]);
     $DEBUG .= "<br />". $sql;
     $crs = pg_query($conn, $sql);
     if (pg_num_rows($crs) > 0) {
       $crow = pg_fetch_array($crs,0);
       $warnings[$key]["counties"] .= sprintf("%s,%s ", $crow["name"], $crow["state"]);
       $warnings[$key]["carea"] += $crow["area"];
       $sum_carea += $crow["area"];
     } else {
       $warnings[$key]["counties"] .= sprintf("%s, ", $key);
     }
  }
}

/* Now we go hunting for LSRs! */
$lsrs = Array();
$ltypeSQL = "";
reset($ltype);
while( list($k,$v) = each($ltype)){ 
 if ($v == "TO") $ltypeSQL .= sprintf("'%s',","T"); 
 else if ($v == "SV") $ltypeSQL .= sprintf("'%s','%s','%s',","H","G","D");
 else if ($v == "MA") $ltypeSQL .= sprintf("'%s','%s',","M","W"); 
 else if ($v == "FF") $ltypeSQL .= sprintf("'%s',","F"); 
}
$ltypeSQL .= "'ZZZ'"; /* Hack */
$sql = sprintf("SELECT distinct *, x(geom) as lon0, y(geom) as lat0, 
        astext(geom) as tgeom 
        from lsrs_%s WHERE wfo = '%s' and 
        valid >= '%s' and valid < '%s' and type in (%s) and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= $hail) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
        ORDER by valid ASC",
        date("Y", $sts), $wfo, $stsSQL, $etsSQL, $ltypeSQL);
$DEBUG .= "<br />". $sql;
$rs = pg_query($conn, $sql);
for ($i=0;$row = @pg_fetch_array($rs,$i);$i++)
{
   $key = sprintf("%s-%s-%s-%s-%s", $row["wfo"], $row["valid"], $row["type"],
          $row["magnitude"], $row["city"]);
  // $q = strtotime($row["valid"]);
  // if ($q < 10000){ print_r($row);  continue; }
   $lsrs[$key] = $row;
   $lsrs[$key]['geom'] = $row["tgeom"];
   $lsrs[$key]["ts"] = strtotime($row["valid"]);
   $lsrs[$key]["warned"] = 0;
   $lsrs[$key]["tdq"] = 0; /* Tornado DQ */
   $lsrs[$key]["leadtime"] = "NA";
   $lsrs[$key]["remark"] = $row["remark"];
}
/* Now we verify warnings!! */
$sw = "";
reset($warnings);
while (list($k,$v) = each($warnings))
{
  if (! isset($v["geom"])){ 
    /* Okay, we must have a polygon to proceed */
    continue;
  }
  $wsts = strtotime($v["issue"]);
  $wstsSQL = gmdate("Y/m/d H:i", $wsts);
  $wets = strtotime($v["expire"]);
  $wetsSQL = gmdate("Y/m/d H:i", $wets);
  $geom = $v["geom"];
  $lw = "";
  /* Now we query LSRS! */  
  $sql = sprintf("SELECT distinct * from lsrs_%s WHERE 
         geom && SetSrid(GeometryFromText('%s'),4326) and 
         contains(SetSrid(GeometryFromText('%s'),4326), geom) 
         and type IN (%s) and wfo = '%s' and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= $hail) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
         and valid >= '%s' and valid <= '%s' ", date("Y", $wsts),
         $geom, $geom, $ltypeSQL, $wfo, $wstsSQL, $wetsSQL);
  $DEBUG .= "<br />". $sql;
  $rs = pg_query($conn, $sql);
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $wfo = $row["wfo"];
    $lType = $row["type"];
    $lMag = $row["magnitude"];
    $key = sprintf("%s-%s-%s-%s-%s", $row["wfo"], $row["valid"], $row["type"],
          $row["magnitude"], $row["city"]);
    /* Now we need to do some checking */
    if ($v["phenomena"] == "FF")
    {
       if ($lType == "F") { /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
    }
    else if ($v["phenomena"] == "TO")
    {
       if ($lType == "T") { /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
       else { /* DQ! */
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["tdq"] = 1;
         $lw .= printLSR($lsrs[$key]);
       }
    }
    else if ($v["phenomena"] == "MA")
    {
       if ($lType == "W") { /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
       else if ($lType == "M" && floatval($lMag) >= 34){ /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
       else if ($lType == "H" && floatval($lMag) >= $hail){ /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }

    }
    else if ($v["phenomena"] == "SV")
    {
       if ($lType == "G" && floatval($lMag) >= 58){ /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
       else if ($lType == "H" && floatval($lMag) >= $hail){ /* Verify! */
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
       else if ($lType == "D") {
         $warnings[$k]["verify"] = 1;
         $lsrs[$key]["warned"] = 1;
         $lsrs[$key]["leadtime"] = ($lsrs[$key]['ts'] - $warnings[$k]['sts']) / 60;
         if ($warnings[$k]["lead0"] < 0) $warnings[$k]["lead0"] = $lsrs[$key]["leadtime"];
         $lw .= printLSR($lsrs[$key]);
       }
    }
  }
  $sw .= printWARN( $warnings[$k] );
  $sw .= $lw;
}

?>

<?php /* Now we worry about those LSRs that did not verify */
$ls = "";
reset($lsrs);
while( list($k,$v) = each($lsrs))
{
  if ($v["warned"] == 1 || $v["tdq"] == 1) { continue; }
  $ls .= printLSR($lsrs[$k]);
}

/* Now we need to compute stats! */

$wcount = sizeof($warnings);
$wverif = 0;
reset($warnings);
$leadcnt = 0;
$leadtotal = 0;
while (list($k,$v) = each($warnings))
{
  if ($v["verify"] == 1){ $wverif += 1; }
  if ($v["lead0"] >= 0)
  {
    $leadcnt += 1;
    $leadtotal += $v["lead0"];
  }
}
if ($leadcnt == 0) { $firstlead = 0; }
else { $firstlead = round($leadtotal / $leadcnt,1); }

if ($wcount == 0) { $wverifpc = 0; $far = 0;}
else { 
 $wverifpc = round( ($wverif / $wcount) * 100, 0); 
 $far = round(($wcount - $wverif) / ($wcount),2);
}


$reports = sizeof($lsrs);

reset($lsrs);
$wevents = 0;
$dqs = 0;
$uwevents = 0;
$leadcnt = 0;
$leadtot = 0;
$leads = Array();
while (list($k,$v) = each($lsrs))
{
  $DEBUG .= "<br /> $k ". $v["warned"];
  if ($v["warned"] == 1 && $v["leadtime"] != "NA"){ 
    $wevents += 1; 
    $leadcnt += 1;
    $leadtot += $v["leadtime"];
    $leads[] = $v["leadtime"];
  }
  else if ($v["warned"] == 0){ $uwevents += 1; }
  if ($v["tdq"] == 1){ $dqs += 1; }
}
if (sizeof($leads) == 0){
  $minlead = 0;
  $maxlead = 0;
  $avglead = 0;
} else {
  $minlead = min($leads);
  $maxlead = max($leads);
  $avglead = round($leadtot / $leadcnt,1);
}
if (($wevents+$uwevents) == 0){  $pod = 0; }
else { $pod = round(($wevents / ($wevents+$uwevents)),2); }
if (($wcount+$uwevents) == 0){ $csi = 0; }
else {
 // $csi = round(floatval($wverif)/ floatval(($wcount+$uwevents)),2); 
 $csi = round(pow((pow($pod,-1) + pow(1-$far,-1) - 1), -1), 2);
}
?>
<h3 class="heading">Summary:</h3>
<?php echo "<b>Begin Date:</b> ". date("m/d/Y H:i", $sts) ." <b>End Date:</b> ". date("m/d/Y H:i", $ets); ?>
<br />* These numbers are not official and should be used for educational purposes only.

<table cellspacing="1" cellpadding="2" border="1">
<tr>
<td>
<?php echo sprintf("<img src=\"chart.php?aw=%s&ae=%s&b=%s&c=%s&d=%s\" align=\"left\">", $wverif, $wevents, $uwevents, $wcount-$wverif, "NA"); ?>
</td>
<td>
 <table cellspacing="0" cellpadding="3" border="1">
 <tr><th>Listed Warnings:</th><th><?php echo $wcount; ?></th></tr>
 <tr><th>Verified: (A<sub>w</sub>)</th><th><?php echo $wverif; ?></th></tr>
 <tr><th>% Verified</th><th><?php echo $wverifpc; ?></th></tr>
 <tr><th>Storm Based Warning Size Reduction:</th>
<th><?php if ($sum_carea > 0) { echo sprintf("%.0f", ($sum_carea - $sum_parea) / $sum_carea * 100);}else{ echo "0";} ?> %</th></tr>
 <tr><th>Avg SBW Size (sq km)</th><th><?php if ($wcount > 0) { echo sprintf("%.0f",  $sum_parea / $wcount); } else { echo "0"; }  ?></th></tr>
 </table>
</td>
<td>
 <table cellspacing="1" cellpadding="2" border="1">
 <tr><th>Reports</th><th><?php echo $reports; ?></th></tr>
 <tr><th>Warned Events (A<sub>e</sub>)</th><th><?php echo $wevents; ?></th></tr>
 <tr><th>Unwarned Events (B)</th><th><?php echo $uwevents; ?></th></tr>
 <tr><th>Non TOR LSRs during TOR warning</th><th><?php echo $dqs; ?></th></tr>
 </table>
</td>
<td><img src="cow.jpg"></td>
</tr>
<tr>
<!-- PARSEME: FAR:<?php echo $far; ?> POD:<?php echo $pod; ?> CSI:<?php echo $csi; ?> -->
<td colspan="4">
 <table cellspacing="1" cellpadding="2" border="1">
 <tr>
 <th>FAR == C / (A<sub>w</sub>+C) = <span style="color: #f00;"><?php echo $far; ?></span></th>
 <th>POD == A<sub>e</sub> / (A<sub>e</sub> + B) = <span style="color: #f00;"><?php echo $pod; ?></span></th>
 <th>CSI == ((POD)<sup>-1</sup> + (1-FAR)<sup>-1</sup> - 1)<sup>-1</sup> = <span style="color: #f00;"><?php echo $csi; ?></span></th>
 </tr>
 </table>
</td>
</tr>
<tr>
<td colspan="3">
 <table cellspacing="1" cellpadding="2" border="1">
 <tr>
 <th>Avg Lead Time for 1rst Event</th><th><?php echo $firstlead; ?></th>
 <th>Avg Lead Time for all Events</th><th><?php echo $avglead; ?></th>
 <th>Max Lead Time</th><th><?php echo $maxlead; ?></th>
 <th>Min Lead Time</th><th><?php echo $minlead; ?></th>
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
<br />The second line is for details on any local storm reports.
<br />
<table cellspacing="0" cellpadding="2" border="1">
<tr><td></td><th>Issued:</th><th>Expired:</th><th colspan="2">County:</th><th>Final Status:</th><th>SBW Area: (P)</th><th>County Area: (C)</th><th>Size %<br /> (C-P)/C:</th><th>Perimeter Ratio:</th></tr>
<tr bgcolor="#eee"><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th><th colspan="3">Remarks</th></tr>
<?php echo $sw; ?>
</table>

<h3 class="heading">Storm Reports without warning:</h3> 
<table cellspacing="1" cellpadding="2" border="1">
<tr><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th></tr>
<?php echo $ls; ?></table>
<?php //echo $DEBUG; ?>
