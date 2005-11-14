<?php
$conn = iemdb("postgis");
pg_query($conn, "SET TIME ZONE 'GMT'");

$stsSQL = date("Y/m/d H:i", $sts);
$etsSQL = date("Y/m/d H:i", $ets);

$DEBUG = "";

function printLSR($lsr)
{
  $lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg", "H" => "Hail","G" => "Wind Gust");
  $background = "#0f0";
  if ($lsr["warned"] == 0) $background = "#f00";
  if ($lsr["leadtime"] == "NA") { $background = "#eee"; $leadtime = "NA"; }
  else {$leadtime = $lsr["leadtime"] ." minutes"; }
  if ($lsr["tdq"] > 0) $background = "#aaa";
  if ($lsr["magnitude"] == 0) $lsr["magnitude"] = "";
  //if ($lsr["ts"] < 100000) print_r($lsr);
  $uri = sprintf("maplsr.phtml?lat0=%s&lon0=%s&ts=%s", $lsr["lat0"], $lsr["lon0"], gmdate("Y-m-d%20H:i", $lsr["ts"]));
  return sprintf("<tr style=\"background: #eee;\"><td>lsr</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td style=\"background: %s;\">%s</td><td>%s,%s</td><td><a href=\"%s\" target=\"_new\">%s</a></td><td>%s</td><td>%s</td></tr>", 
    $uri, gmdate("m/d/Y H:i", $lsr["ts"]), $background, $leadtime, $lsr["county"], $lsr["state"], $uri, $lsr["city"], $lt[$lsr["type"]], $lsr["magnitude"]);
}
function printWARN($warn)
{
  $background = "#0f0";
  $ts = $warn["sts"] + 5*60;
  $uri = sprintf("/GIS/apps/rview/cat.phtml?wfo=%s&event_id=%s&phenomena=%s", $warn["wfo"], $warn["eventid"], $warn["phenomena"]);
  $uri2 = sprintf("/GIS/apps/rview/warnings.phtml?tz=UTC&cu=1&year=%s&month=%s&day=%s&hour=%s&minute=%s&filter=1&archive=yes&tzoff=0&site=%s&lon0=%s&lat0=%s", gmdate("Y", $ts), gmdate("m", $ts), gmdate("d",$ts), gmdate("H",$ts), gmdate("i",$ts), $warn["wfo"], $warn["lon0"], $warn["lat0"]);
  if ($warn["verify"] == 0) $background = "#f00";
  return sprintf("<tr><td style=\"background: %s;\"><a href=\"%s\">%s</a></td><td>%s</td><td>%s</td><td colspan=\"2\"><a href=\"%s\" target=\"_new\">%s</a></td><td><a href=\"%s\">%s</a></td><td>%.0f km^2</td></tr>", 
       $background, $uri, $warn["phenomena"], gmdate("m/d/Y H:i", $warn["sts"]), gmdate("m/d/Y H:i", $warn["ets"]), 
       $uri2, $warn["counties"], $uri, $warn["status"], $warn["area"]);

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
    xmax(geom) as lon0, ymax(geom) as lat0 from 
    warnings_%s WHERE wfo = '%s' and issue >= '%s' and expire < '%s' 
    and phenomena IN (%s) and significance = 'W' ORDER by issue ASC) as foo) as foo",
   date("Y", $sts), $wfo, $stsSQL, $etsSQL, $wtypeSQL);
$DEBUG .=  "<br />". $sql;
$rs = pg_query($conn, $sql);
for ($i=0;$row = @pg_fetch_array($rs,$i);$i++)
{
  $key = sprintf("%s-%s-%s", $row["wfo"], $row["phenomena"], $row["eventid"]);
  if ( ! isset($warnings[$key]) ){ $warnings[$key] = Array(); }
  $warnings[$key]["issue"] = $row["issue"];
  $warnings[$key]["expire"] = $row["expire"];
  $warnings[$key]["phenomena"] = $row["phenomena"];
  $warnings[$key]["wfo"] = $row["wfo"];
  $warnings[$key]["status"] = $row["status"];
  $warnings[$key]["area"] = $row["area"];
  $warnings[$key]["lat0"] = $row["lat0"];
  $warnings[$key]["lon0"] = $row["lon0"];
  $warnings[$key]["sts"] = strtotime($row["issue"]);
  $warnings[$key]["ets"] = strtotime($row["expire"]);
  $warnings[$key]["eventid"] = $row["eventid"];
  $warnings[$key]["lead0"] = -1;
  if ($row["gtype"] == "P"){ 
    $warnings[$key]["geom"] = $row["tgeom"]; 
    $warnings[$key]["gtype"] = $row["gtype"];
  }
  $warnings[$key]["verify"] = 0;
  if ($row["gtype"] == "C")
  {
     $sql = sprintf("SELECT * from nws_ugc WHERE ugc = '%s'", $row["ugc"]);
     $DEBUG .= "<br />". $sql;
     $crs = pg_query($conn, $sql);
     $crow = pg_fetch_array($crs,0);
     if (! isset($warnings[$key]["counties"]) ) $warnings[$key]["counties"] = "";
     $warnings[$key]["counties"] .= sprintf("%s,%s ", $crow["name"], $crow["state"]);
  }
}

/* Now we go hunting for LSRs! */
$lsrs = Array();
$ltypeSQL = "";
reset($ltype);
while( list($k,$v) = each($ltype)){ 
 if ($v == "TO") $ltypeSQL .= sprintf("'%s',","T"); 
 else if ($v == "SV") $ltypeSQL .= sprintf("'%s','%s','%s',","H","G","D");
 else if ($v == "FF") $ltypeSQL .= sprintf("'%s',","F"); 
}
$ltypeSQL .= "'ZZZ'"; /* Hack */
$sql = sprintf("SELECT distinct *, x(geom) as lon0, y(geom) as lat0, 
        astext(geom) as tgeom 
        from lsrs WHERE wfo = '%s' and 
        valid >= '%s' and valid < '%s' and type in (%s) and
        (type = 'F' or (type = 'H' and magnitude >= $hail) or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D')
        ORDER by valid ASC",
        $wfo, $stsSQL, $etsSQL, $ltypeSQL);
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
}
/* Now we verify warnings!! */
$sw = "";
reset($warnings);
while (list($k,$v) = each($warnings))
{
  $wsts = strtotime($v["issue"]);
  $wstsSQL = gmdate("Y/m/d H:i", $wsts);
  $wets = strtotime($v["expire"]);
  $wetsSQL = gmdate("Y/m/d H:i", $wets);
  $geom = $v["geom"];
  $lw = "";
  /* Now we query LSRS! */  
  $sql = sprintf("SELECT distinct * from lsrs WHERE 
         geom && SetSrid(GeometryFromText('%s'),4326) and 
         contains(SetSrid(GeometryFromText('%s'),4326), geom) 
         and type IN (%s) and wfo = '%s'
         and valid >= '%s' and valid <= '%s' ",
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
    if ($v["phenomena"] == "TO")
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
    else if ($v["phenomena"] == "FF")
    {
       if ($lType == "D") {
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
<?php echo "Begin Date: ". date("m/d/Y H:i", $sts) ." End Date: ". date("m/d/Y H:i", $ets); ?>
<h3 class="heading">Summary:</h3>

<table cellspacing="1" cellpadding="2" border="1">
<tr>
<td>
<?php echo sprintf("<img src=\"chart.php?aw=%s&ae=%s&b=%s&c=%s&d=%s\" align=\"left\">", $wverif, $wevents, $uwevents, $wcount-$wverif, "NA"); ?>
</td>
<td>
 <table cellspacing="1" cellpadding="2" border="1">
 <tr><th>Listed Warnings:</th><th><?php echo $wcount; ?></th></tr>
 <tr><th>Verified: (A<sub>w</sub>)</th><th><?php echo $wverif; ?></th></tr>
 <tr><th>% Verified</th><th><?php echo $wverifpc; ?></th></tr>
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
<td><img src="panda.jpg"></td>
</tr>
<tr>
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
<table cellspacing="1" cellpadding="2" border="1">
<tr><td></td><th>Issued:</th><th>Expired:</th><th colspan="2">County:</th><th>Final Status:</th><th>Poly Area:</th></tr>
<tr bgcolor="#eee"><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th></tr>
<?php echo $sw; ?>
</table>
<h3 class="heading">Storm Reports without warning:</h3> 
<table cellspacing="1" cellpadding="2" border="1">
<tr><th>lsr</th><th>Valid</th><th>Lead Time:</th><th>County</th><th>City</th><th>Type</th><th>Magnitude</th></tr>
<?php echo $ls; ?></table>
<?php // echo $DEBUG; ?>
