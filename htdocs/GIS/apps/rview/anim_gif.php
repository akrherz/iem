<?php
/* Create animated GIF! and then send it to them... */

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

$fts = isset($_GET["fts"]) ? intval($_GET["fts"]) : exit();

$memcache = new Memcached();
$memcache->addServer('iem-memcached.local', 11211);
$urls = $memcache->get("/GIS/apps/rview/warnings.phtml?fts=${fts}");
if (!$urls) {
    die("fts not found, ERROR");
}
chdir("/var/webtmp");
$cmdstr = "gifsicle --colors 256 --loopcount=0 --delay=100 -o ${fts}_anim.gif ";
foreach ($urls as $k => $v) {
    // value is now single quoted, so remove those
    $res = file_get_contents(sprintf(
        "http://iem.local%s",
        str_replace("'", "", $v)
    ));
    $fn = "{$fts}_{$k}.png";
    $gfn = "{$fts}_{$k}.gif";
    $f = fopen($fn, 'wb');
    fwrite($f, $res);
    fclose($f);
    `convert $fn $gfn`;
    $cmdstr .= " {$gfn} ";
}

`$cmdstr`;

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=myanimation.gif");

readfile("${fts}_anim.gif");
