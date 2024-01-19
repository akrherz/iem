<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";
require_once "../../../include/network.php";

/** We need these vars to make this work */
$syear = isset($_GET["syear"]) ? $_GET["syear"] : date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"] : date("m");
$sday = isset($_GET["sday"]) ? $_GET["sday"] : date("d");
$days = isset($_GET["days"]) ? $_GET["days"] : 2;
$station = isset($_GET['station']) ? $_GET["station"] : "";
$network = isset($_GET["network"]) ? $_GET["network"] : "IA_RWIS";
$nt = new NetworkTable($network);

$sts = time() - (3. * 86400.);
$ets = time();

/** Lets assemble a time period if this plot is historical */
$sts = mktime(0, 0, 0, $smonth, $sday, $syear);
$ets = $sts + ($days * 86400.0);

$iemdb = iemdb('iem');
$rs = pg_prepare($iemdb, "SELECTMETA", "SELECT * from 
      rwis_traffic_meta WHERE nwsli = $1");
$rs = pg_execute($iemdb, "SELECTMETA", array($station));
$avg_speed = array();

$normal_vol = array();
$long_vol = array();
$occupancy = array();
$times = array();
$labels = array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $avg_speed[$row["lane_id"]] = array();
    $normal_vol[$row["lane_id"]] = array();
    $long_vol[$row["lane_id"]] = array();
    $occupancy[$row["lane_id"]] = array();
    $times[$row["lane_id"]] = array();
    $labels[$row["lane_id"]] = $row["name"];
}

$dbconn = iemdb('rwis');
$rs = pg_prepare($dbconn, "SELECT", "SELECT * from alldata_traffic
  WHERE station = $1 and valid > $2 and valid < $3 ORDER by valid ASC");
$rs = pg_execute($dbconn, "SELECT", array(
    $station,
    date("Y-m-d H:i", $sts), date("Y-m-d H:i", $ets)
));

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $times[$row["lane_id"]][] = strtotime(substr($row["valid"], 0, 16));
    $avg_speed[$row["lane_id"]][] = $row["avg_speed"];
    $normal_vol[$row["lane_id"]][] = $row["avg_headway"];
    $long_vol[$row["lane_id"]][] = $row["avg_headway"];
    $occupancy[$row["lane_id"]][] = $row["avg_headway"];
}
pg_close($dbconn);
pg_close($iemdb);


if (pg_num_rows($rs) == 0) {
    $led = new DigitalLED74();
    $led->StrokeNumber('NO TRAFFIC DATA AVAILABLE', LEDC_GREEN);
    die();
}

$cities = $nt->table;

// Create the graph. These two calls are always required
$graph = new Graph(650, 550, "example1");
$graph->SetScale("datlin");
$graph->SetMarginColor("white");
$graph->SetColor("lightyellow");
$graph->img->SetMargin(40, 55, 105, 105);

$graph->yaxis->SetTitle("Average Speed [mph]");
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);

//$graph->xaxis->SetTitle("Time Period: " . date('Y-m-d h:i A', $times[0][0]) . " thru " . date('Y-m-d h:i A', max($times[0])));
$graph->xaxis->SetTitleMargin(67);
$graph->xaxis->title->SetColor("brown");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M-j h A", true);

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);

$colors = array(
    0 => "green", 1 => "black", 2 => "blue", 3 => "red",
    4 => "purple", 5 => "tan", 6 => "pink", 7 => "lavendar"
);
foreach ($times as $k => $v) {
    if (sizeof($times[$k]) < 2) {
        continue;
    }
    // Create the linear plot
    $lineplot = new LinePlot($avg_speed[$k], $times[$k]);
    $lineplot->SetLegend($labels[$k]);
    $lineplot->SetColor($colors[$k]);
    $lineplot->SetWeight(3);
    $graph->add($lineplot);
}

$graph->Stroke();
