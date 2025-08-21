<?php
require_once "../config/settings.inc.php";
require_once "../include/memcache.php";
define("IEM_APPID", 60);
require_once "../include/database.inc.php";

$cached_rss = cacheable("/rss.php", 600)(function(){
    global $EXTERNAL_BASEURL;
    $bd = date('D, d M Y H:i:s O');
    $s = <<<EOM
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<atom:link href="{$EXTERNAL_BASEURL}/rss.php" rel="self" type="application/rss+xml" />
<title>IEM News and Notes</title>
<link>{$EXTERNAL_BASEURL}</link>
<description>Iowa Environmental Mesonet News and Notes</description>
<lastBuildDate>{$bd}</lastBuildDate>
EOM;
    $conn = iemdb("mesosite");
    $rs = pg_exec($conn, "SELECT id, title, body from news ORDER by entered DESC LIMIT 20");
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        // Properly escape the title for XML; previous logic only replaced '&'.
        $title = htmlspecialchars($row["title"], ENT_XML1 | ENT_COMPAT, 'UTF-8');
        // Guard against a body containing the CDATA termination sequence.
        $body = str_replace("]]>", "]]]><![CDATA[>", $row["body"]);
        $s .= "<item>\n";
        $s .= "<title>{$title}</title>\n";
        $s .= "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
        $s .= "<link>{$EXTERNAL_BASEURL}/onsite/news.phtml?id=" . $row["id"] . "</link>\n";
        $s .= "<guid>{$EXTERNAL_BASEURL}/onsite/news.phtml?id=" . $row["id"] . "</guid>\n";
        $s .= "<description><![CDATA[" . $body . "]]></description>\n";
        $s .= "</item>\n";
    }
    $s .= "</channel>\n";
    $s .= "</rss>\n";
    return $s;
});


header("Content-type: text/xml; charset=UTF-8");
echo $cached_rss();