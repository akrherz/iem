<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

/** We need these vars to make this work */
$syear = get_int404("syear", date("Y"));
$smonth = get_int404("smonth", date("m"));
$sday = get_int404("sday", date("d"));
$days = get_int404("days", 2);
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_RWIS";
$nt = new NetworkTable($network);

$sts = time() - (3. * 86400.);
$ets = time();

/** Lets assemble a time period if this plot is historical */
$sts = mktime(0, 0, 0, $smonth, $sday, $syear);
$ets = $sts + ($days * 86400.0);

$iemdb = iemdb('iem');
$stname = iem_pg_prepare($iemdb, "SELECT * from rwis_traffic_meta WHERE nwsli = $1");
$rs = pg_execute($iemdb, $stname, array($station));
$avg_speed = array();

$normal_vol = array();
$long_vol = array();
$occupancy = array();
$times = array();
$labels = array();
while ($row = pg_fetch_assoc($rs)) {
    $avg_speed[$row["lane_id"]] = array();
    $normal_vol[$row["lane_id"]] = array();
    $long_vol[$row["lane_id"]] = array();
    $occupancy[$row["lane_id"]] = array();
    $times[$row["lane_id"]] = array();
    $labels[$row["lane_id"]] = $row["name"];
}

$dbconn = iemdb('rwis');
$stname = uniqid("SELECT");
pg_prepare($dbconn, $stname, "SELECT * from alldata_traffic " .
    "WHERE station = $1 and valid > $2 and valid < $3 ORDER by valid ASC");
$rs = pg_execute($dbconn, $stname, array(
    $station,
    date("Y-m-d H:i", $sts),
    date("Y-m-d H:i", $ets)
));

while ($row = pg_fetch_assoc($rs)) {
    $times[$row["lane_id"]][] = strtotime(substr($row["valid"], 0, 16));
    $avg_speed[$row["lane_id"]][] = $row["avg_speed"];
    $normal_vol[$row["lane_id"]][] = $row["avg_headway"];
    $long_vol[$row["lane_id"]][] = $row["avg_headway"];
    $occupancy[$row["lane_id"]][] = $row["avg_headway"];
}


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
    0 => "green",
    1 => "black",
    2 => "blue",
    3 => "red",
    4 => "purple",
    5 => "tan",
    6 => "pink",
    7 => "lavendar"
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
