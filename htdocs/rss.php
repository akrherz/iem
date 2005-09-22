<?php
 include("../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
 echo "<rss version=\"2.0\">\n";
 echo "<channel>\n";
 echo "<title>Iowa Environmental Mesonet</title>\n";
 echo "<link>http://mesonet.agron.iastate.edu</link>\n";
 echo "<description>
  Iowa Environmental Mesonet News and Notes
</description>\n";
 echo "<lastBuildDate>". date("c") ."</lastBuildDate>\n";
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT * from news ORDER by entered DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
  echo "<item>\n";
  echo "<title>". $row["title"] ."</title>\n";
  echo "<author>". $row["author"] ."</author>\n";
  echo "<link>http://mesonet.agron.iastate.edu/onsite/news.phtml?id=". $row["id"] ."</link>\n";
  echo "</item>\n";
 }
 echo "</channel>\n";
 echo "</rss>\n";
?>
