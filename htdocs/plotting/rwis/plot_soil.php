<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/network.php";

/** We need these vars to make this work */
$syear = get_int404("syear", date("Y"));
$smonth = get_int404("smonth", date("m"));
$sday = get_int404("sday", date("d"));
$days = get_int404("days", 2);
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_RWIS";
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";

$sts = time() - (3. * 86400.);
$ets = time();

$times = array();
$depths = Array(1, 3, 6, 9, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72);
$data = array();
// initialize the data array for each depth
foreach($depths as $depth){
    $data["s{$depth}temp"] = array();
}

$sts = mktime(0, 0, 0, $smonth, $sday, $syear);
$ets = $sts + ($days * 86400.0);

$dbconn = iemdb('rwis');
$rs = pg_prepare($dbconn, "SELECT", "SELECT * from alldata_soil
WHERE station = $1 and valid > $2 and valid < $3 ORDER by valid ASC");
$rs = pg_execute($dbconn, "SELECT", array(
    $station,
    date("Y-m-d H:i", $sts), date("Y-m-d H:i", $ets)
));

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $times[] = strtotime(substr($row["valid"], 0, 16));
    foreach ($depths as $j) {
        $data["s{$j}temp"][] = $row["tmpf_{$j}in"];
    }
}
pg_close($dbconn);

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

if (pg_num_rows($rs) == 0) {
    $led = new DigitalLED74();
    $led->StrokeNumber('NO SOIL DATA AVAILABLE', LEDC_GREEN);
    die();
}

$nt = new NetworkTable($network);
$cities = $nt->table;

// Create the graph. These two calls are always required
$graph = new Graph(650, 550, "example1");
$graph->SetScale("datlin");
$graph->SetMarginColor("white");
$graph->SetColor("lightyellow");
//$graph->img->SetMargin(40,55,105,105);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->title->Set($cities[$station]['name'] . " RWIS Soil Probe Data");
$graph->subtitle->Set("Values at 15 different depths [inch] shown");

$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);

//$graph->xaxis->SetTitle("Time Period:");
$graph->xaxis->SetTitleMargin(67);
$graph->xaxis->title->SetColor("brown");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M-j h A", true);

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->SetColumns(3);

foreach ($depths as $j) {
    // Create the linear plot
    $lineplot = new LinePlot($data["s{$j}temp"], $times);
    $lineplot->SetLegend($j);
    $lineplot->SetWeight(3);
    $graph->add($lineplot);
}

$graph->Stroke();
