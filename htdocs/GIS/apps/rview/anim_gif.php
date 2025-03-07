<?php
require_once "../../../../config/settings.inc.php";
// Create animated GIF! and then send it to them...
require_once "../../../../include/memcache.php";

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

$fts = isset($_GET["fts"]) ? intval($_GET["fts"]) : exit();

$memcache = MemcacheSingleton::getInstance();
$urls = $memcache->get("/GIS/apps/rview/warnings.phtml?fts={$fts}");
if (!$urls) {
    die("fts not found, ERROR");
}
chdir("/var/webtmp");
$cmdstr = "gifsicle --colors 256 --loopcount=0 --delay=100 -o {$fts}_anim.gif ";
foreach ($urls as $k => $v) {
    // value is now single quoted, so remove those
    $res = file_get_contents(sprintf(
        "%s%s",
        $INTERNAL_BASEURL,
        str_replace("'", "", $v)
    ));
    $fn = "{$fts}_{$k}.png";
    $gfn = "{$fts}_{$k}.gif";
    $f = fopen($fn, 'wb');
    fwrite($f, $res);
    fclose($f);
    if (exec(escapeshellcmd("magick $fn $gfn")) === FALSE) {  // skipcq
        die("magick failed");
    };
    $cmdstr .= " {$gfn} ";
}

if (exec(escapeshellcmd($cmdstr)) === FALSE){  // skipcq
    die("gifsicle failed");
};

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=myanimation.gif");

readfile("{$fts}_anim.gif");
