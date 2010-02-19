<?php
 include("../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
 echo "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n";
 echo "<channel>\n";
 echo "<atom:link href=\"http://mesonet.agron.iastate.edu/feature_rss.php\" rel=\"self\" type=\"application/rss+xml\" />\n";
 echo "<title>Iowa Environmental Mesonet Daily Feature</title>\n";
 echo "<link>http://mesonet.agron.iastate.edu</link>\n";
 echo "<description>
  Iowa Environmental Mesonet Daily Feature
</description>\n";
 echo "<lastBuildDate>". date('D, d M Y h:i:s O') ."</lastBuildDate>\n";
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref from feature ORDER by valid DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
  $cbody = "<img src=\"http://mesonet.agron.iastate.edu/onsite/features/". $row["imageref"] ."_s.png\" alt=\"Feature\" style=\"float: left; padding: 5px;\"/>". $row["story"];
  $cbody = ereg_replace("&","&amp;", $cbody);
  $cbody = ereg_replace(">","&gt;", $cbody);
  $cbody = ereg_replace("<","&lt;", $cbody);
  echo "<item>\n";
  echo "<title>". ereg_replace("&","&amp;",$row["title"]) ."</title>\n";
  echo "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
  echo "<link>http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". substr($row["valid"],0,10) ."</link>\n";
  echo "<guid>http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". substr($row["valid"],0,10) ."</guid>\n";
  echo "<description>". $cbody ."</description>\n";
  echo "</item>\n";
 }
 echo "</channel>\n";
 echo "</rss>\n";
?>
