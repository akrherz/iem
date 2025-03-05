<?php
require_once "../config/settings.inc.php";
require_once "../include/memcache.php";
define("IEM_APPID", 60);
require_once "../include/database.inc.php";

$cached_rss = cacheable("/rss.php", 600)(function(){
    $bd = date('D, d M Y H:i:s O');
    $s = <<<EOM
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<atom:link href="https://mesonet.agron.iastate.edu/rss.php" rel="self" type="application/rss+xml" />
<title>IEM News and Notes</title>
<link>https://mesonet.agron.iastate.edu</link>
<description>Iowa Environmental Mesonet News and Notes</description>
<lastBuildDate>{$bd}</lastBuildDate>
EOM;
    $conn = iemdb("mesosite");
    $rs = pg_exec($conn, "SELECT * from news ORDER by entered DESC LIMIT 20");
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $s .= "<item>\n";
        $s .= "<title>" . str_replace("&", "&amp;", $row["title"]) . "</title>\n";
        $s .= "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
        $s .= "<link>https://mesonet.agron.iastate.edu/onsite/news.phtml?id=" . $row["id"] . "</link>\n";
        $s .= "<guid>https://mesonet.agron.iastate.edu/onsite/news.phtml?id=" . $row["id"] . "</guid>\n";
        $s .= "<description><![CDATA[" . $row["body"] . "]]></description>\n";
        $s .= "</item>\n";
    }
    $s .= "</channel>\n";
    $s .= "</rss>\n";
    return $s;
});


header("Content-type: text/xml; charset=UTF-8");
echo $cached_rss();