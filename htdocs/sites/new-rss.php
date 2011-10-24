<?php 
/* RSS Feed of new IEM added station tables, default to 25 long?
 * $Id$:
 */
 include("../../config/settings.inc.php");
 define("IEM_APPID", 37);
 include("$rootpath/include/database.inc.php");
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT s.*, x(geom) as lon, y(geom) as lat, t.name as netname from stations s JOIN networks t 
 	ON (t.id = s.network) ORDER by iemid DESC LIMIT 25");
 pg_close($conn);
 
 
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
 echo "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n";
 echo "<channel>\n";
 echo "<atom:link href=\"http://mesonet.agron.iastate.edu/sites/new-rss.php\" rel=\"self\" type=\"application/rss+xml\" />\n";
 echo "<title>Iowa Environmental Mesonet - New Stations</title>\n";
 echo "<link>http://mesonet.agron.iastate.edu/sites/locate.php</link>\n";
 echo "<description>
  RSS feed of new stations added to IEM metadata tables...
</description>\n";
 echo "<lastBuildDate>". date('D, d M Y H:i:s O') ."</lastBuildDate>\n";
 
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
 	$cbody = "<pre>\n";
 	$cbody .= "ID     : ". $row["id"] ."\n";
 	$cbody .= "Name   : ". $row["name"] ."\n";
	$cbody .= "Lat    : ". $row["lat"] ."\n";
    $cbody .= "Lon    : ". $row["lon"] ."\n";
    $cbody .= "Ele [m]: ". $row["elevation"] ."\n";
    $cbody .= "Network: ". $row["netname"] ."(". $row["network"] .")\n";
 	$cbody .= "</pre>\n";
  echo "<item>\n";
  echo "<title>". $row["name"] ." [". $row["id"] ."]</title>\n";
  echo "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
  echo "<link>http://mesonet.agron.iastate.edu/sites/site.php?station=". $row["id"] ."&amp;network=". $row["network"] ."</link>\n";
  echo "<guid>http://mesonet.agron.iastate.edu/sites/site.php?station=". $row["id"] ."&amp;network=". $row["network"] ."</guid>\n";
  echo "<description>". $cbody ."</description>\n";
  echo "</item>\n";
 }
 echo "</channel>\n";
 echo "</rss>\n";

?>