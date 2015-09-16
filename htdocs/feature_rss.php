<?php
 include("../config/settings.inc.php");
 define("IEM_APPID", 62);
 header("Content-type: text/xml; charset=UTF-8");
 
 $memcache = new Memcache;
 $memcache->connect('iem-memcached', 11211);
 $val = $memcache->get("/feature_rss.php");
 if ($val){
 	die($val);
 }
 // Need to buffer the output so that we can save it to memcached later
 ob_start();
 
 include("../include/database.inc.php");
 $d = date('D, d M Y H:i:s O');
 echo <<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<atom:link href="http://mesonet.agron.iastate.edu/feature_rss.php" rel="self" type="application/rss+xml" />
<title>Iowa Environmental Mesonet Daily Feature</title>
<link>http://mesonet.agron.iastate.edu</link>
<description>Iowa Environmental Mesonet Daily Feature</description>
<lastBuildDate>{$d}</lastBuildDate>
EOF;
 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref from feature ORDER by valid DESC LIMIT 20");
 pg_close($conn);
 for ($i=0; $row = @pg_fetch_assoc($rs, $i); $i++) {
	$appurl = "";
 	if ($row["appurl"] != ""){
		$appurl = "<p><a href=\"https://mesonet.agron.iastate.edu".$row["appurl"]."\">Generate This Chart on IEM Website</a></p>";
	}
 	$cbody = <<<EOF
<img src="https://mesonet.agron.iastate.edu/onsite/features/{$row["imageref"]}.png" 
 alt="Feature" style="float: left; padding: 5px;" />
 <p>{$row["story"]}</p>
 {$appurl}
EOF;
  $t = $row["title"];
  $v = substr($row["valid"],0,10);
  echo <<<EOF
<item>
<title><![CDATA[{$t}]]></title>
<author>akrherz@iastate.edu (Daryl Herzmann)</author>
<link>http://mesonet.agron.iastate.edu/onsite/features/cat.php?day={$v}</link>
<guid>http://mesonet.agron.iastate.edu/onsite/features/cat.php?day={$v}</guid>
<description><![CDATA[{$cbody}]]></description>
</item>
EOF;
 }
 echo "</channel>\n";
 echo "</rss>\n";
 
 $memcache->set("/feature_rss.php", ob_get_contents(), false, 3600); // one hour
 ob_end_flush();
 
?>
