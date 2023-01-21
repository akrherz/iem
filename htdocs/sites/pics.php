<?php
/*
 * My purpose in life is to produce pics
 */
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;
$t = new MyView();

$dir = isset($_GET["dir"]) ? xssafe($_GET["dir"]) : "";

$filename = "/mesonet/share/pics/{$station}/{$station}.jpg";
$puri = "pics/{$station}/{$station}.jpg";

if ($dir != "") {
    $filename = "/mesonet/share/pics/{$station}/{$station}_{$dir}.jpg";
    $puri = "pics/{$station}/{$station}_{$dir}.jpg";
}
if (!file_exists($filename)) {
    $puri = '/images/nophoto.png';
}
$t->title = "Site Photos";

$t->sites_current = "pics";

$table = sprintf(
    "<tr>%s%s%s</tr><tr>%s%s%s</tr><tr>%s%s%s</tr>",
    $ctx->printtd("NW", $dir),
    $ctx->printtd("N", $dir),
    $ctx->printtd("NE", $dir),
    $ctx->printtd("W", $dir),
    "<td><img src=\"{$puri}\" alt=\"{$station} {$dir}\" class=\"img img-responsive\" /></td>",
    $ctx->printtd("E", $dir),
    $ctx->printtd("SW", $dir),
    $ctx->printtd("S", $dir),
    $ctx->printtd("SE", $dir)
);

$more = "";
$filename = "/mesonet/share/pics/{$station}/{$station}_span.jpg";
$puri = "pics/{$station}/{$station}_span.jpg";
$lfilename = "/mesonet/share/pics/{$station}/{$station}_pan.jpg";
$pluri = "pics/{$station}/{$station}_pan.jpg";
if (file_exists($filename)) {
    $more = "<h3>Panoramic Shot</h3><img src=\"$puri\"><br /><a href=\"$pluri\">Full resolution version</a>";
}
if (file_exists("/mesonet/share/pics/$station/HEADER.html")) {
    $more .= "<p><strong>" . file_get_contents("/mesonet/share/pics/$station/HEADER.html") . "</strong>";
}

$t->content = <<<EOF
<h3>Directional Photos</h3>

<p>This application shows you photos of the observation site if they are
available.  In general, the IEM only has photos for some of the sites in 
Iowa...</p>

<p><a href="pics.php?network={$network}&station={$station}">Site Photo</a>

<table>
{$table}
</table>

{$more}
EOF;
$t->render('sites.phtml');
