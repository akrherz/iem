<?php
require_once "../config/settings.inc.php";
require_once "../include/memcache.php";
define("IEM_APPID", 60);
require_once "../include/database.inc.php";

$cached_rss = cacheable("/rss.php", 600)(function(){
    global $EXTERNAL_BASEURL;
    $conn = iemdb("mesosite");
    $rs = pg_query(
        $conn,
        "SELECT id, title, body, entered from news ORDER by entered DESC LIMIT 20"
    );
    $rows = [];
    while ($row = pg_fetch_assoc($rs)) {
        $rows[] = $row;
    }
    $bd = date('D, d M Y H:i:s O');
    if (!empty($rows[0]["entered"])) {
        $ts = strtotime($rows[0]["entered"]);
        if ($ts !== false) {
            $bd = date('D, d M Y H:i:s O', $ts);
        }
    }
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
    for ($i = 0; $row = $rows[$i] ?? null; $i++) {
        // Properly escape the title for XML; previous logic only replaced '&'.
        $title = htmlspecialchars($row["title"], ENT_XML1 | ENT_COMPAT, 'UTF-8');
        // Guard against a body containing the CDATA termination sequence.
        $body = str_replace("]]>", "]]]><![CDATA[>", $row["body"]);
        $itemDate = date('D, d M Y H:i:s O');
        if (!empty($row["entered"])) {
            $itemTs = strtotime($row["entered"]);
            if ($itemTs !== false) {
                $itemDate = date('D, d M Y H:i:s O', $itemTs);
            }
        }
        $s .= "<item>\n";
        $s .= "<title>{$title}</title>\n";
        $s .= "<author>akrherz@iastate.edu (Daryl Herzmann)</author>\n";
        $s .= "<link>{$EXTERNAL_BASEURL}/onsite/news.phtml?id=" . $row["id"] . "</link>\n";
        $s .= "<guid>{$EXTERNAL_BASEURL}/onsite/news.phtml?id=" . $row["id"] . "</guid>\n";
        $s .= "<pubDate>{$itemDate}</pubDate>\n";
        $s .= "<description><![CDATA[" . $body . "]]></description>\n";
        $s .= "</item>\n";
    }
    $s .= "</channel>\n";
    $s .= "</rss>\n";
    return $s;
});


header("Content-Type: application/rss+xml; charset=UTF-8");
echo $cached_rss();
