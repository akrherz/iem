<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
 $site = isset($_GET["site"]) ? substr($_GET["site"],0,3): "DMX";
 $loop = isset($_GET["loop"]) ? $_GET["loop"]: "";
 $fips = isset($_GET["fips"]) ? $_GET["fips"]: "";

 $TITLE = "IEM GIS | RADAR & NWS Warnings";
 $REFRESH = "<meta http-equiv=\"refresh\" content=\"600; URL=$rooturl/GIS/apps/iawarn/iawarn.php?site=${site}\">";
 $THISPAGE = "current-radar"; include("$rootpath/include/header.php");
?>
<div class="text">
<?php
$width = "450";
$height = "450";


include("$rootpath/include/mlib.php");
include("$rootpath/include/currentOb.php");
include("$rootpath/include/nexlib2.php");
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
$r2d2= Array();
//$fcontents = file('/mesonet/data/gis/images/unproj/'.$site.'/'.$site.'.log');
//while (list ($line_num, $line) = each ($fcontents)) {
//  $radTimes[$line_num] = substr($line,0,12);
//}
for($l=0;$l<10;$l++)
{
  $ts = filemtime("/home/ldm/data/gis/images/4326/$site/n0r_$l.tif");
  $radTimes[] = $ts;
  $r2d2[] = date("h:i a", $ts);
}

//$lastT = $radTimes[8];
//$radTS = substr($radTimes[8], 4, 2) ."/". substr($radTimes[8], 6, 2) ." ". substr($radTimes[8], 8, 4) ."Z";

include("iawarn2.php");

if (strlen($loop) > 0){

  $urls = Array();

  for ($i=0;$i<9;$i++){
   $imgi = $i;
   $radValid = $radTimes[$i];
   $urls[$i] = drawRADAR($site, $imgi, $extents, $projs, $radValid, $fips);
  }

  //echo "<br><b>Last Image Valid at:</b> ". $radTS;
  include ("loop.php");
  $urls = array_reverse($urls);
  $r2d2 = array_reverse($r2d2);
  printHTML($urls, $r2d2);
} else {
  $radValid = $radTimes[8];
  $imgi = 0;
  $url = drawRADAR($site, $imgi, $extents, $projs, $radValid, $fips);

 //echo "<br><b>Valid at:</b> ". $radTS;

echo "<br><center><img src=\"". $url ."\" border=\"1\" width=\"450\"></center>\n";

}

echo "
  </td></tr>\n</table>
</td></tr>\n</table>\n";


//$fcontents = file('/mesonet/data/gis/images/unproj/'.$site.'/'.$site.'.log');
//while (list ($line_num, $line) = each ($fcontents)) {
//  $lastT = $line;
//}

$connection = iemdb("postgis");

$query = "SELECT w.eventid, w.wfo, w.phenomena, w.oid, u.name as cname, w.expire as expire, 
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

  $t = $row["phenomena"];
  if (isset($afos[$t])) $t = $afos[$row["phenomena"]] ;

  $caturl = "$rooturl/GIS/apps/rview/warnings_cat.phtml?year=". strftime("%Y", $issue) ."&wfo=". $row["wfo"] ."&phenomena=". $row["phenomena"] ."&eventid=". $row["eventid"] ;
  echo "<tr> <td><a href=\"". $caturl ."\">$t</a></td> 
    <td>". $row["cname"] ."</td> 
    <td>". $row["sname"] ."</td>
    <td>". strftime("%I:%M %p", $issue) ."</td>
    <td>". strftime("%I:%M %p", $expire) ."</td>
    </tr>\n";

}

echo "</table></div>\n";


 include ("$rootpath/include/footer.php");
?>
