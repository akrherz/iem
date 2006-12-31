<?php
 include("../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
 echo "<rss version=\"2.0\">\n";
 echo "<channel>\n";
 echo "<title>Iowa Environmental Mesonet Daily Feature</title>\n";
 echo "<link>http://mesonet.agron.iastate.edu</link>\n";
 echo "<description>
  Iowa Environmental Mesonet Daily Feature
</description>\n";
 echo "<lastBuildDate>". date("c") ."</lastBuildDate>\n";
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT * from feature ORDER by valid DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
  echo "<item>\n";
  echo "<title>". ereg_replace("&","&amp;",$row["title"]) ."</title>\n";
  echo "<author>Daryl Herzmann</author>\n";
  echo "<link>http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". substr($row["valid"],0,10) ."</link>\n";
  echo "</item>\n";
 }
 echo "</channel>\n";
 echo "</rss>\n";
?>
