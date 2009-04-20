<?php
 include("../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 header("Content-type: text/xml");
 echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
 echo "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n";
 echo "<channel>\n";
 echo "<atom:link href=\"http://mesonet.agron.iastate.edu/rss.php\" rel=\"self\" type=\"application/rss+xml\" />\n";
 echo "<title>Iowa Environmental Mesonet</title>\n";
 echo "<link>http://mesonet.agron.iastate.edu</link>\n";
 echo "<description>
  Iowa Environmental Mesonet News and Notes
</description>\n";
 echo "<lastBuildDate>". date('D, d M Y h:i:s O')  ."</lastBuildDate>\n";
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT * from news ORDER by entered DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_array($rs, $i); $i++) {
  echo "<item>\n";
  echo "<title>". ereg_replace("&","&amp;",$row["title"]) ."</title>\n";
  echo "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
  echo "<link>http://mesonet.agron.iastate.edu/onsite/news.phtml?id=". $row["id"] ."</link>\n";
  echo "<guid>http://mesonet.agron.iastate.edu/onsite/news.phtml?id=". $row["id"] ."</guid>\n";
  if ( intval($row["id"]) < 830){
    echo "<description>&lt;pre&gt;". $row["body"] ."&lt;/pre&gt;</description>\n";
  } else {
    echo "<description>". htmlentities($row["body"]) ."</description>\n";
  }
  echo "</item>\n";
 }
 echo "</channel>\n";
 echo "</rss>\n";
?>
