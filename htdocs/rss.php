<?php
 require_once "../config/settings.inc.php";
 header("Content-type: text/xml; charset=UTF-8");
 
 $memcache = new Memcached();
 $memcache->addServer('iem-memcached', 11211);
 $val = $memcache->get("/rss.php");
 if ($val){
 	die($val);
 }
 // Need to buffer the output so that we can save it to memcached later
 ob_start();
 
 
 define("IEM_APPID", 60);
 require_once "../include/database.inc.php";
 
 $bd = date('D, d M Y H:i:s O');
 echo <<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<atom:link href="https://mesonet.agron.iastate.edu/rss.php" rel="self" type="application/rss+xml" />
<title>IEM News and Notes</title>
<link>https://mesonet.agron.iastate.edu</link>
<description>Iowa Environmental Mesonet News and Notes</description>
<lastBuildDate>{$bd}</lastBuildDate>
EOF;
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT * from news ORDER by entered DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_assoc($rs, $i); $i++) {
  echo "<item>\n";
  echo "<title>". preg_replace("&","&amp;",$row["title"]) ."</title>\n";
  echo "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
  echo "<link>https://mesonet.agron.iastate.edu/onsite/news.phtml?id=". $row["id"] ."</link>\n";
  echo "<guid>https://mesonet.agron.iastate.edu/onsite/news.phtml?id=". $row["id"] ."</guid>\n";
  echo "<description><![CDATA[". $row["body"] ."]]></description>\n";
  echo "</item>\n";
 }
echo "</channel>\n";
echo "</rss>\n";

$memcache->set("/rss.php", ob_get_contents(), 600); // ten minutes
ob_end_flush();

?>
