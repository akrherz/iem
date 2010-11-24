<?php
$loop = $_GET["loop"];
if (strlen($loop) == 0) $loop = 0;
if (strlen($loop) == "Yes") $loop = 1;
?>
<html>
<head>
  <title>IEM GIS | RADAR & NWS Warnings</title>
  <link rel="stylesheet" type="text/css" href="/css/main.css">
  <meta http-equiv="refresh" content="600; URL=iawarn.php?site=<?php echo $site; ?>&loop=<?php echo $loop; ?>">
</head>
<?php
 include ("../../../include/header2.php");
?>
<b>Nav:</b> <a href="/current/">Current Data</a> <b> > </b>
  NEXRAD & Warnings<br>

<?php
$width = "640";
$height = "480";


include('../../../include/mlib.php');
include('../../../include/currentOb.php');
include('../../../include/allLoc.php');
include('../../../include/nexlib.php');

if (strlen($site) == 0){
 $site = "DMX";
}

?>

<table bgcolor="black" width="100%" cellpadding=2 border=0 cellspacing=0>
  <tr><td>
<table width="100%" bgcolor="white" cellpadding=2 border=0 cellspacing=0>
  <tr><td valign="TOP" bgcolor="#dddddd">

<form method="GET" action="iawarn.php">
<b>Select View:</b>
<select name="site">
<?php
while( list($key, $value) = each($wfos) ){
  echo "<option value=\"$key\" ";
  if ($site == $key) echo "SELECTED";
  echo ">$value \n";
}
?>
</select>

<b>Loop?:</b>
<select name="loop">
  <option value="0" <?php if ($loop == 0) echo "SELECTED"; ?>">No
  <option value="1" <?php if ($loop == 1) echo "SELECTED"; ?>">Java Script
  <option value="2" <?php if ($loop == 1) echo "SELECTED"; ?>">Applet
</select>

<input type="submit" value="Show Map">
</form>
</td></tr>

<tr><td>

<?php

echo "<p><b>NEXRAD Site:</b> ". $wfos[$site] ." (".$site.")</p>\n";

$radTimes = Array();
$fcontents = file('/mesonet/data/gis/'.$site.'.log');
while (list ($line_num, $line) = each ($fcontents)) {
  $radTimes[$line_num] = substr($line,0,13);
}
$lastT = $radTimes[8];
$radTS = substr($radTimes[8], 4, 2) ."/". substr($radTimes[8], 6, 2) ." ". substr($radTimes[8], 9, 4) ."Z";

if (intval($loop) ==  1){

  $urls = Array();

  for ($i=0;$i<9;$i++){
   $imgi = 8 - $i;
   $radValid = $radTimes[$i];
   include("iawarn2.php");
   $urls[$i] = $url;
  }

  echo "<b>Last Image Valid at:</b> ". $radTS;
  include ("loop.php");
  array_reverse($urls);
  printHTML($urls, $radTimes);
} else {
  $radValid = $radTimes[8];
  $imgi = 0;
  include("iawarn2.php");

 echo "<b>Valid at:</b> ". $radTS;

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
echo "<br><center><img src=\"". $url ."\" border=\"1\"></center>\n";

}

echo "
  </td></tr>\n</table>
</td></tr>\n</table>\n";


$fcontents = file('/mesonet/data/gis/'.$site.'.log');
while (list ($line_num, $line) = each ($fcontents)) {
  $lastT = $line;
}

$connection = pg_connect("host=iemdb port=5432 dbname=postgis user=mesonet");

$query = "SELECT w.type, w.oid, u.name as cname, w.expire as expire, 
  w.issue as issue, s.state_name as sname from warnings w, uscounties u, states s
  WHERE w.expire > '".$db_ts."' 
   and w.gtype = 'C' and w.fips = u.fips 
  and u.state_fips = s.state_fips ORDER by issue DESC";

$result = pg_exec($connection, $query);

pg_close($connection);

$afos = Array("SVR" => "Severe Thunderstorm",
  "TOR" => "Tornado",
  "FFW" => "Flash Flood");

echo "<table width=\"100%\">
<tr>
  <th>Warning:</th><th>County</th><th>State</th><th>Issued:</th>
  <th>Expires:</th></tr>
";

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
  $issue = strtotime($row["issue"]);
  $expire = strtotime($row["expire"]);

  echo "<tr> <td><a href=\"cat.php?id=". $row["oid"] ."\"> ". $afos[$row["type"]] ."</a></td> 
    <td>". $row["cname"] ."</td> 
    <td>". $row["sname"] ."</td>
    <td>". strftime("%I:%M %p", $issue) ."</td>
    <td>". strftime("%I:%M %p", $expire) ."</td>
    </tr>\n";

}

echo "</table>\n";


 include ("../../../include/footer2.php");
?>
