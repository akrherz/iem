<?php
/* Fails when no polygon warning was present with the warning
   ex) CAR.SV.9.2007
*/
if (! isset($sts) ) {
    header("Location: /cow/");
    die(); /* Avoid direct calls.... */
}

function printLSR($lsr, $verified=FALSE)
{
    $valid = new DateTime($lsr["valid"]);
    $lt = Array(
        "F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg",
        "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout",
        "M" => "Marine Tstm Wnd", "2" => "Dust Storm");
    $background = ($lsr["warned"] == False) ? "#f00" : "#0f0";
    if (is_null($lsr["leadtime"])) {
        $background = "#eee";
        $leadtime = "NA";
    } else {
        $leadtime = $lsr["leadtime"] ." minutes";
    }
    if (array_key_exists("__assoc__", $lsr)){
        $background = "#8FBC8F";
    }
    if ($lsr["tdq"] || ! $verified) {
        $background = "#aaa";
    }
    if ($lsr["magnitude"] == 0) {
        $lsr["magnitude"] = "";
    }
    $uri = sprintf("/lsr/#%s/%s/%s", $lsr["wfo"], $valid->format("YmdHi"),
        $valid->format("YmdHi") );
    return sprintf(
        '<tr style="background: #eee;"><td></td>'.
        '<td><a href="%s" target="_new">%s</a></td>'.
        '<td style="background: %s;">%s</td><td>%s,%s</td>'.
        '<td><a href="%s" target="_new">%s</a></td><td>%s</td><td>%s</td>'.
        '<td colspan="5">%s</td></tr>',
	    $uri, $valid->format("m/d/Y H:i"), $background, $leadtime,
	    $lsr["county"], $lsr["state"], $uri, $lsr["city"],
	    $lt[strval($lsr["type"])], $lsr["magnitude"], $lsr["remark"]);
}

function printWARN($lsrs, $warn)
{
    global $lsrbuffer;
    $issue = new DateTime($warn["issue"]);
    $expire = new DateTime($warn["expire"]);
    $uri = sprintf(
        "/vtec/#%s-O-%s-K%s-%s-%s-%04d",
        $issue->format("Y"), 
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

    $s = sprintf(
        "<tr><td style=\"background: %s;\"><a href=\"%s\">%s.%s</a>%s</td>
  		<td>%s</td><td>%s</td>
  		<td colspan=\"2\"><a href=\"%s\" target=\"_new\">%s</a></td>
  		<td><a href=\"%s\">%s</a></td><td>%.0f sq km</td>
  		<td>%.0f sq km</td><td>%.0f %%</td>
  		<td>%.0f%% <a href=\"/GIS/radmap.php?layers[]=legend&layers[]=ci&layers[]=cbw&layers[]=sbw&layers[]=uscounties&layers[]=bufferedlsr&vtec=%s.K%s.%s.%s.%04d&lsrbuffer=%s\">Visual</a></td>
  		<td>%.0f%%</td><td>%s</td></tr>\n", 
        $background, $uri, $warn["phenomena"], $warn["eventid"], $windhail,
        $issue->format("m/d/Y H:i"),
        $expire->format("m/d/Y H:i"), 
        $uri, implode(", ", $warn["ar_ugcname"]), $uri,
        $warn["status"], $warn["parea"], 
        $warn["carea"],
        ($warn["carea"] - $warn["parea"])/ $warn["carea"]  * 100,
        $bratio,
        $issue->format("Y"), $warn["wfo"], $warn["phenomena"],
        $warn["significance"], $warn["eventid"], $lsrbuffer,
        $warn["areaverify"] / $warn["parea"] * 100., $warn["fcster"]);

    $all_lsrs = explode(",", $warn["stormreports_all"]);
    $verif_lsrs = explode(",", $warn["stormreports"]);
    foreach($lsrs as $k => $lsr){
        if (! in_array($lsr["id"], $all_lsrs)){
            continue;
        }
        $verified = in_array($lsr["id"], $verif_lsrs);
        // Recompute the lead time as this LSR may have a leadtime based on
        // an earlier warning
        $lsrvalid = new DateTime($lsr["properties"]["valid"]);
        $leadtime = (
            intval($lsrvalid->diff($issue)->format("%h")) * 60 +
            intval($lsrvalid->diff($issue)->format("%i"))
        );
        if ($leadtime != $lsr["properties"]["leadtime"]){
            $lsr["properties"]["leadtime"] = $leadtime;
            $lsr["properties"]["__assoc__"] = True;
        }

        $s .= printLSR($lsr["properties"], $verified);
    }
    return $s;
}

$phenoms = "";
foreach($wtype as $k => $w){
    $phenoms .= sprintf("&phenomena=%s", $w);
}
$lsrtypes = "";
foreach($ltype as $k => $w){
    $lsrtypes .= sprintf("&lsrtype=%s", $w);
}

// Build Cow API URL
$wsuri = sprintf(
    "http://iem.local/api/1/cow.json?wfo=%s&begints=%sZ&".
    "endts=%sZ&hailsize=%s&wind=%s%s%s&lsrbuffer=%s&warningbuffer=%s",
    (strlen($wfo) == 4) ? substr($wfo, 1, 3): $wfo,
    $sts->format("Y-m-d\\TH:i:00"),
    $ets->format("Y-m-d\\TH:i:00"),
    $hail,
    $wind,
    $phenoms,
    $lsrtypes,
    $lsrbuffer,
    floatval($warnbuffer) * 100., // approx to km
);
if ($fcster != ''){
    $wsuri .= sprintf("&fcster=%s", $fcster);
}
if (isset($useWindHailTag) && $useWindHailTag == 'Y'){
    $wsuri .= "&windhailtag=Y";
}
if (isset($limitwarns) && $limitwarns == 'Y'){
    $wsuri .= "&limitwarns=Y";
}

$res = file_get_contents($wsuri);
if ($res === FALSE) {
    echo <<< EOM
<h3>IEM Cow API Error</h3>

<p>Sorry, the backend service for your request had an unexpected failure.  Please
consider contacting daryl, akrherz@iastate.edu and copy/paste the long URL that
appears at the top of this webpage for his review and fix!</p>
EOM;
    die();
}
$jobj = json_decode($res, True);
$stats = $jobj['stats'];

$charturl = sprintf(
    "chart.php?aw=%s&ae=%s&b=%s&c=%s&d=%s",
    $stats["events_verified"], $stats["warned_reports"],
    $stats["unwarned_reports"], $stats["events_total"] - $stats["events_verified"],
    "NA");

if (sizeof($ltype) == 0){
	$content .= "<div class='warning'>You did not select any of the Local Storm 
	Report types above, so none are listed below...<br /><br /></div>";
}
if (sizeof($wtype) == 0){
	$content .= "<div class='warning'>You did not select any of the Warning 
	types above, so none are listed below...<br /><br /></div>";
}

$dstat = $sts->format("m/d/Y H:i");
$dstat1 = $ets->format("m/d/Y H:i");

$aw = sprintf("%s", $stats["events_verified"]);
$pv = sprintf("%.1f", $stats["events_verified"] / $stats["events_total"] * 100);
$sr = sprintf("%.1f", 100 - $stats["size_poly_vs_county[%]"]);
$asz =  sprintf("%.0f", $stats["avg_size[sq km]"]);
$av = sprintf("%.0f", $stats["area_verify[%]"]);

$ae = $stats["warned_reports"];
$b = $stats["unwarned_reports"];
$tdq = $stats["tdq_stormreports"];

$wtable = "";
$wsz = sizeof($jobj["events"]["features"]);
$stormreports = $jobj["stormreports"]["features"];
foreach($jobj["events"]["features"] as $k => $warn){
	$wtable .= printWARN($stormreports, $warn["properties"]);
}

$ltable = "";
$lsz = sizeof($stormreports);
foreach($stormreports as $k => $lsr){
	if ($lsr["properties"]["warned"]) {
        continue;
    }
	$ltable .= printLSR($lsr["properties"]);
}
$far = sprintf("%.2f", $stats["FAR[1]"]);
$pod = sprintf("%.2f", $stats["POD[1]"]);
$csi = sprintf("%.2f", $stats["CSI[1]"]);

$aleadtime = sprintf("%.1f", $stats["avg_leadtime_firstreport[min]"]);
$allleadtime = sprintf("%.1f", $stats["avg_leadtime[min]"]);
$maxleadtime = sprintf("%.1f", $stats["max_leadtime[min]"]);
$minleadtime = sprintf("%.1f", $stats["min_leadtime[min]"]);

$fwarning = "";
if ($fcster != ''){
	$fwarning = <<<EOF
<div class="alert alert-warning">
	<strong>This display is filtered for product signature: "{$fcster}".
	This means that the 'Unwarned Events' are not accurate as they may have
	verified by warnings signed by a different string.</strong></div>
EOF;
}

$shpuri = sprintf(
    "/cgi-bin/request/gis/watchwarn.py?year1=%s&amp;".
    "month1=%s&amp;day1=%s&amp;hour1=%s&amp;minute1=0&amp;year2=%s&amp;".
    "month2=%s&amp;".
    "day2=%s&amp;hour2=%s&amp;minute2=0&amp;limit1=yes&amp;wfo[]=%s",
    $sts->format("Y"), $sts->format("m"), $sts->format("d"),
    $sts->format("H"), $ets->format("Y"), $ets->format("m"), $ets->format("d"),
    $ets->format("H"), $wfo);

$lsruri = sprintf(
    '/cgi-bin/request/gis/lsr.py?wfo[]=%s&amp;sts=%sZ&amp;ets=%sZ',
    $wfo, $sts->format("Y-m-d\\TH:i"), $ets->format("Y-m-d\\TH:i"),
);

$content .= <<<EOF
<strong>Related Downloads:</strong>
<a href="{$wsuri}" class="btn btn-primary">JSON Web Service</a> &nbsp;
<a href="{$shpuri}" class="btn btn-primary">Shapefile of Warnings</a> &nbsp;
<a href="{$lsruri}" class="btn btn-primary">Shapefile of LSRs</a> &nbsp;

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
 <tr><th>Local Storm Reports</th><th>{$lsz}</th></tr>
 <tr><th>Warned Local Storm Reports (A<sub>e</sub>)</th><th>{$ae}</th></tr>
 <tr><th>Unwarned Local Storm Reports (B)</th><th>{$b}</th></tr>
 <tr><th>LSRs during TOR warning without SVR warning</th><th>{$tdq}</th></tr>
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

<h3>Warnings Issued & Verifying LSRs:</h3>
<strong>Column Headings:</strong> 
<i>Issued:</i> UTC timestamp of when the product was issued, 
<i>Expired:</i> UTC timestamp of when the product expired,
<i>Final Status:</i> VTEC action of the last statement issued for the product,
<i>SBW Area:</i> Size of the storm based warning in square km,
<i>County Area:</i> Total size of the counties included in the product in square km,
<i>Size % (C-P)/C:</i> Size reduction gained by the storm based warning,
<i>Perimeter Ratio:</i> Estimated percentage of the storm based warning polygon border that was influenced by political boundaries (0% is ideal).
<i>Areal Verification %:</i> Percentage of the polygon warning that received a verifying report (report is buffered {$lsrbuffer} km).

<table class="table-condensed">
<tr><th>LSR Leadtime Color Key</th>
<td style="background: #0F0;">LSR verified warning</td>
<td style="background: #8FBC8F;">LSR covered by earlier warning</td>
<td style="background: #AAA;">LSR non-verifying type for warning</td>
</table>

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
