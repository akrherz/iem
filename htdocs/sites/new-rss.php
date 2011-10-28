<?php 
/* RSS Feed of new IEM added station tables, default to 25 long?
 * $Id$:
 */
 include("../../config/settings.inc.php");
 define("IEM_APPID", 37);
 include("$rootpath/include/database.inc.php");
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT s.*, x(geom) as lon, y(geom) as lat, t.name as netname from stations s JOIN networks t 
 	ON (t.id = s.network) WHERE s.elevation > -990 ORDER by iemid DESC LIMIT 25");
 pg_close($conn);
 
 
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
 echo "<feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:georss=\"http://www.georss.org/georss\">\n";
 echo "<title>Iowa Environmental Mesonet - New Stations GeoRSS</title>\n";
 echo "<subtitle>Iowa Environmental Mesonet - New Stations GeoRSS</subtitle>\n";
 echo "<link href=\"http://mesonet.agron.iastate.edu/sites/locate.php\" />\n";
 echo "<updated>". gmdate('Y-m-d\\TH:i:s\\Z') ."</updated>\n";
 echo "<id>http://mesonet.agron.iastate.edu/sites/locate.php</id>\n";
 echo "<author><name>Daryl Herzmann</name><email>akrherz@iastate.edu</email></author>\n";
 
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
 	$cbody = "<pre>\n";
 	$cbody .= "ID     : ". $row["id"] ."\n";
 	$cbody .= "Name   : ". $row["name"] ."\n";
	$cbody .= "Lat    : ". $row["lat"] ."\n";
    $cbody .= "Lon    : ". $row["lon"] ."\n";
    $cbody .= "Ele [m]: ". $row["elevation"] ."\n";
    $cbody .= "Network: ". $row["netname"] ."(". $row["network"] .")\n";
 	$cbody .= "</pre>\n";
 	$cbody = ereg_replace("&","&amp;", $cbody);
    $cbody = ereg_replace(">","&gt;", $cbody);
    $cbody = ereg_replace("<","&lt;", $cbody);
  echo "<entry>\n";
  echo "<title>". $row["name"] ." [". $row["id"] ."]</title>\n";
  echo "<author><name>Daryl Herzmann</name><email>akrherz@iastate.edu</email></author>\n";
  echo "<link href=\"http://mesonet.agron.iastate.edu/sites/site.php?station=". $row["id"] ."&amp;network=". $row["network"] ."\" />\n";
  echo "<content type=\"html\">". $cbody ."</content>\n";
  echo "<id>http://mesonet.agron.iastate.edu/sites/site.php?station=". $row["id"] ."&amp;network=". $row["network"] ."</id>\n";
  echo "<updated>". gmdate('Y-m-d\\TH:i:s\\Z', strtotime($row["modified"])) ."</updated>\n";
  echo "<georss:point>". $row["lat"] ." ". $row["lon"] ."</georss:point>\n";
  echo "</entry>\n";
 }
 echo "</feed>\n";

?>