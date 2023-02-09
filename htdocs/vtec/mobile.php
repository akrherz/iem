<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/myview.php";
$conn = iemdb("postgis");

$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';
openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
syslog(LOG_WARNING, "Deprecated " . $_SERVER["REQUEST_URI"] .
    ' remote: ' . $_SERVER["REMOTE_ADDR"] .
    ' referer: ' . $ref);
closelog();

$v = isset($_GET["vtec"]) ? substr($_GET["vtec"], 0, 25) : "2008-O-NEW-KJAX-TO-W-0048";
$tokens = preg_split("/-/", $v);
$year = intval($tokens[0]);
$operation = $tokens[1];
$vstatus = $tokens[2];
$wfo4 = $tokens[3];
$wfo = substr($wfo4, 1, 3);
$phenomena = $tokens[4];
$significance = $tokens[5];
$eventid = intval($tokens[6]);

$title = sprintf(
    "%s %s %s #%s",
    $wfo,
    $vtec_phenomena[$phenomena],
    $vtec_significance[$significance],
    $eventid
);
// Get the product text
$rs = pg_prepare($conn, "SELECT", "SELECT replace(report,'\001','') as report,
        replace(svs,'\001','') as svs
        from warnings_$year w WHERE w.wfo = $1 and 
        w.phenomena = $2 and w.eventid = $3 and 
        w.significance = $4 ORDER by length(svs) DESC LIMIT 1");

$rs = pg_execute($conn, "SELECT", array($wfo, $phenomena, $eventid, $significance));
$txtdata = "";
for ($i = 0; $row  = pg_fetch_array($rs); $i++) {
    if (!is_null($row["svs"])){
        $tokens = explode('__', $row["svs"]);
        $tokens = array_reverse($tokens);
        foreach ($tokens as $key => $val) {
            if ($val == "") continue;
            $txtdata .= sprintf("<pre>%s</pre><br />", $val);
        }
    }
    $txtdata .= sprintf(
        "<h4>Issuance Report:</h4><pre>%s</pre><br />",
        $row["report"]
    );
}

$imgurl = sprintf(
    "/GIS/radmap.php?layers[]=uscounties&amp;layers[]=sbw" .
        "&amp;layers[]=nexrad&amp;width=640&amp;height=480&amp;vtec=%s",
    str_replace('-', '.', $v)
);

$t = new MyView();
$t->title = $title;
$t->content = <<<EOF
<h3>{$title}</h3>

<img src="{$imgurl}" class="img img-responsive" alt="VTEC Image"/>

<h3>NWS Text Data</h3>

{$txtdata}
EOF;

$t->render('single.phtml');
