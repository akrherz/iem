<?php
/* Generate GR placefile of webcam stuff */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/cameras.inc.php";
require_once "../../../include/iemprop.php";
require_once "../../../include/forms.php";
$camera_refresh = get_iemprop("webcam.interval");
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "KCCI";
$overview = isset($_GET["overview"]);

$thres = 999;
$title = "IEM Webcam Overview";
if (!$overview) {
    $thres = 45;
    $title = "$network webcams via IEM";
}
header("Content-type: text/plain");
$r = floatval($camera_refresh) / 60;
echo "Refresh: $r
Threshold: $thres
Title: $title
IconFile: 1, 15, 25, 8, 25, \"http://www.spotternetwork.org/icon/arrows.png\"
";

$conn = iemdb("mesosite");

$sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval) and cam != 'KCRG-014' and cam !~* 'IDOT'";
$s2 = "";
$s3 = "";
$q = 2;
$vectors = array(
    "E" => array("ax" => 320, "ay" => 120),
    "S" => array("ax" => 160, "ay" => 240),
    "W" => array("ax" => 0, "ay" => 120),
    "N" => array("ax" => 160, "ay" => 0)
);

$rs = pg_exec($conn, $sql);
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $key = $row["cam"];
    if (!$overview && $cameras[$key]["network"] != $network) {
        continue;
    }
    $drct = $row["drct"];
    if ($drct >= 315 || $drct < 45) {
        $v = $vectors["N"];
    } else if ($drct >= 45 && $drct < 135) {
        $v = $vectors["E"];
    } else if ($drct >= 135 && $drct < 225) {
        $v = $vectors["S"];
    } else {
        $v = $vectors["W"];
    }

    if (!$overview)
        echo sprintf("IconFile: %s, 320, 240, %.0f, %.0f,\"https://mesonet.agron.iastate.edu/data/camera/stills/%s.jpg\"\n", $q, $v["ax"], $v["ay"], $key);
    if ($overview)
        $s2 .= sprintf("Icon: %.4f,%.4f,%s,1,7,\"[%s] %s\"\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $drct, $key, $cameras[$key]["name"]);
    if (!$overview)
        $s3 .= sprintf("Icon: %.4f,%.4f,000,%s,1\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $q);
    $q += 1;
}
echo $s2;
if (!$overview)
    echo $s3;
