<?php
/* USED BY /DCP/plot.js :( 
 * JSONP service for IEM Tracked network metadata
 */
header('content-type: application/json; charset=utf-8');
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";

$network = isset($_REQUEST["network"]) ? $_REQUEST["network"] : "KCCI";
$nt = new NetworkTable($network);

$ar = array("stations" => array());

foreach ($nt->table as $sid => $data) {
    $z = array(
        "id" => $sid,
        "combo" => sprintf("[%s] %s", $sid, $data["name"]),
        "name" => $data["name"],
        "lon" => $data["lon"],
        "lat" => $data["lat"]
    );
    $ar["stations"][] = $z;
}

$json = json_encode($ar);

// JSON if no callback
if (!isset($_REQUEST['callback']))
    exit($json);

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";
