<?php
require_once "../../../config/settings.inc.php";

$uri = $_SERVER['REQUEST_URI'];
// Replace any station[] with stations
$uri = preg_replace('/station%5B%5D/', 'stations', $uri);
$pos = strpos($uri, '?');
if ($pos !== false) {
    $uri = substr($uri, $pos + 1);
}
header("Location: /cgi-bin/request/coopobs.py?$uri");