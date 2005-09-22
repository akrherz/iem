<?php
 $TITLE = "IEM GIS | RADAR & NWS Warnings";
 $REFRESH = "<meta http-equiv=\"refresh\" content=\"600; URL=http://mesonet.agron.iastate.edu/GIS/apps/iawarn/iawarn.php?site=${site}\">";
 include("/mesonet/php/include/header.php");
?>
<div class="text">
<b>Nav:</b> <a href="/current/radar.phtml">Current RADAR Data</a> <b> > </b>
  NEXRAD & Warnings<br>

<?php
$width = "450";
$height = "450";

dl("php_mapscript_401.so");
include('../../../include/mlib.php');
include('../../../include/currentOb.php');
include('../../../include/allLoc.php');
include('../../../include/nexlib2.php');

if (strlen($site) == 0){
 $site = "DMX";
}

?>

<table bgcolor="black" width="100%" cellpadding=2 border=0 cellspacing=0>
  <tr><td>
<table width="100%" bgcolor="white" cellpadding=2 border=0 cellspacing=0>
  <tr><td valign="TOP" bgcolor="#dddddd" width="200">

<table width="100%" border=0 cellpadding=2 cellspacing=0>
<tr>
  <th colspan=2>Select RADAR:</th>
</tr>

<tr>
  <td><a href="iawarn.php?site=ABR">ABR - Aberdeen</a></td>
  <td><a href="iawarn.php?site=ABR&loop=yes">(Loop)</a></td>
</tr>
<tr bgcolor="#EEEEEE">
  <td><a href="iawarn.php?site=ARX">ARX - LaCrosse</a></td>
  <td><a href="iawarn.php?site=ARX&loop=yes">(Loop)</a></td>
</tr>
<tr>
  <td><a href="iawarn.php?site=DMX">DMX - Des Moines</a></td>
  <td><a href="iawarn.php?site=DMX&loop=yes">(Loop)</a></td>
</tr>
<tr bgcolor="#EEEEEE">
  <td><a href="iawarn.php?site=DVN">DVN - Davenport</a></td>
  <td><a href="iawarn.php?site=DVN&loop=yes">(Loop)</a></td>
</tr>
<tr>
  <td><a href="iawarn.php?site=EAX">EAX - Pleasant Hill</a></td>
  <td><a href="iawarn.php?site=EAX&loop=yes">(Loop)</a></td>
</tr>
<tr bgcolor="#EEEEEE">
  <td><a href="iawarn.php?site=FSD">FSD - Sioux Falls</a></td>
  <td><a href="iawarn.php?site=FSD&loop=yes">(Loop)</a></td>
</tr>
<tr>
  <td><a href="iawarn.php?site=MPX">MPX - Minneapolis</a></td>
  <td><a href="iawarn.php?site=MPX&loop=yes">(Loop)</a></td>
</tr>
<tr bgcolor="#EEEEEE">
  <td><a href="iawarn.php?site=OAX">OAX - Omaha</a></td>
  <td><a href="iawarn.php?site=OAX&loop=yes">(Loop)</a></td>
</tr>
<tr>
  <td><a href="iawarn.php?site=UDX">UDX - Rapid City</a></td>
  <td><a href="iawarn.php?site=UDX&loop=yes">(Loop)</a></td>
</tr>


</table>

<p>While this application can provide useful information, its purpose 
is purely educational.  Errors can and do occur.

</td><td width="500">

<?php

echo "<p><b>NEXRAD Site:</b> ". $wfos[$site] ." (".$site.")</p>\n";

$radTimes = Array();
$fcontents = file('/mesonet/data/gis/images/unproj/'.$site.'/'.$site.'.log');
while (list ($line_num, $line) = each ($fcontents)) {
  $radTimes[$line_num] = substr($line,0,12);
}
$lastT = $radTimes[8];
$radTS = substr($radTimes[8], 4, 2) ."/". substr($radTimes[8], 6, 2) ." ". substr($radTimes[8], 8, 4) ."Z";

include("iawarn2.php");

if (strlen($loop) > 0){

  $urls = Array();

  for ($i=0;$i<9;$i++){
   echo $i;
   $imgi = 8 - $i;
   $radValid = $radTimes[$i];
   $urls[$i] = drawRADAR($site, $imgi, $extents, $projs, $radValid, $fips);
  }

  echo "<br><b>Last Image Valid at:</b> ". $radTS;
  include ("loop.php");
  array_reverse($urls);
  printHTML($urls, $radTimes);
} else {
  $radValid = $radTimes[8];
  $imgi = 0;
  $url = drawRADAR($site, $imgi, $extents, $projs, $radValid, $fips);

 echo "<br><b>Valid at:</b> ". $radTS;

/**
 echo "<form method=\"GET\" action=\"cat.php\">\n";
 echo "<input type=\"hidden\" value=\"".$site."\" name=\"site\">\n";
 echo "<input type=\"hidden\" value=\"".($Srect->minx)."\" name=\"lon_ll\">\n";
 echo "<input type=\"hidden\" value=\"".($Srect->miny)."\" name=\"lat_ll\">\n";
 echo "<input type=\"hidden\" value=\"".($Srect->maxx)."\" name=\"lon_ur\">\n";
 echo "<input type=\"hidden\" value=\"".($Srect->maxy)."\" name=\"lat_ur\">\n";
 echo "<input border=2 name=\"img\" type=\"image\" src=\"". $url ."\">\n";
 echo "</form>\n";
*/
echo "<br><center><img src=\"". $url ."\" border=\"1\" width=\"450\"></center>\n";

}

echo "
  </td></tr>\n</table>
</td></tr>\n</table>\n";


$fcontents = file('/mesonet/data/gis/images/unproj/'.$site.'/'.$site.'.log');
while (list ($line_num, $line) = each ($fcontents)) {
  $lastT = $line;
}

$connection = pg_connect("host=10.10.10.40 port=5432 dbname=postgis user=mesonet");

$query = "SELECT w.phenomena, w.oid, u.name as cname, w.expire as expire, 
  w.issue as issue, s.state_name as sname from warnings w, nws_ugc u, states s
  WHERE w.expire > CURRENT_TIMESTAMP 
   and w.gtype = 'C' and u.ugc = w.ugc 
  and u.state = s.state_abbr ORDER by issue DESC";

$result = pg_exec($connection, $query);

pg_close($connection);

$afos = Array("SV" => "Severe Thunderstorm",
  "TO" => "Tornado",
  "FF" => "Flash Flood");

echo "<table width=\"100%\">
<tr>
  <th>Warning:</th><th>County</th><th>State</th><th>Issued:</th>
  <th>Expires:</th></tr>
";

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
  $issue = strtotime($row["issue"]);
  $expire = strtotime($row["expire"]);

  echo "<tr> <td><a href=\"cat.php?id=". $row["oid"] ."\"> ". $afos[$row["phenomena"]] ."</a></td> 
    <td>". $row["cname"] ."</td> 
    <td>". $row["sname"] ."</td>
    <td>". strftime("%I:%M %p", $issue) ."</td>
    <td>". strftime("%I:%M %p", $expire) ."</td>
    </tr>\n";

}

echo "</table></div>\n";


 include ("/mesonet/php/include/footer.php");
?>
