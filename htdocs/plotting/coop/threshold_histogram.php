<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_plotline.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$conn = iemdb("coop");
$station1 = isset($_GET["station1"]) ? substr(xssafe($_GET["station1"]), 0, 6) : 'IA0200';
$station2 = isset($_GET["station2"]) ? substr(xssafe($_GET["station2"]), 0, 6) : '';

$slimiter = "and station = '$station1'";
if ($station1 == "iowa") {
    $slimiter = "";
}
$nt = new NetworkTable("IACLIMATE");

if (!array_key_exists($station1, $nt->table)) {
    http_response_code(422);
    die("Unknown station identifier");
}
if ($station2 != '' && !array_key_exists($station2, $nt->table)) {
    http_response_code(422);
    die("Unknown station identifier");
}

$xdata = array();
$ydata = array();
$stname = uniqid("select0");
pg_prepare($conn, $stname, "SELECT y1, count(*) from 
          ((SELECT year as y1, low from alldata_ia 
           WHERE month IN (12) $slimiter) UNION 
          (SELECT year - 1 as y1, low from alldata_ia 
           WHERE month IN (1,2) $slimiter)) as foo 
         WHERE low < $1 GROUP by y1");
for ($thres = -40; $thres < 11; $thres++) {
    $rs = pg_execute($conn, $stname, array($thres));
    $xdata[] = $thres;
    $ydata[] = pg_num_rows($rs);
}
// get the last value from ydata
$yrs = $ydata[count($ydata) - 1];
if ($yrs == 0) {
    die("No data found for this station");
}
$pct = array();
foreach ($ydata as $k => $v) {
    $pct[] = $v / $yrs * 100.0;
}


if ($station2 != "") {
    $slimiter = "and station = '$station2'";
    $ydata = array();
    $stname = uniqid("select1");
    pg_prepare($conn, $stname, "SELECT y1, count(*) from 
          ((SELECT year as y1, low from alldata_ia 
           WHERE month IN (12) $slimiter) UNION 
          (SELECT year - 1 as y1, low from alldata_ia 
           WHERE month IN (1,2) $slimiter)) as foo 
         WHERE low < $1 GROUP by y1");
    for ($thres = -40; $thres < 11; $thres++) {
        $rs = pg_execute($conn, $stname, array($thres));
        $ydata[] = pg_num_rows($rs);
    }
    $yrs2 = $ydata[count($ydata) - 1];
    $pct2 = array();
    foreach ($ydata as $k => $v) {
        $pct2[] = $v / $yrs2 * 100.0;
    }
}

$cities = $nt->table;

$graph = new Graph(500, 400);
$graph->SetScale("lin");
$graph->img->SetMargin(40, 10, 50, 0);

$graph->title->Set("Winter [DJF] Low Temp Thresholds");

$graph->yaxis->SetTitle("Percentage of years");
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);

$graph->xaxis->SetTitle("Low Temperature [F] Threshold");
$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);

$graph->legend->Pos(0.5, 0.07);

for ($i = -30; $i < 10; $i = $i + 10) {
    $graph->AddLine(new PlotLine(VERTICAL, $i, "tan", 1));
}

$lineplot2 = new LinePlot($pct, $xdata);
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3);
$lineplot2->SetLegend("$yrs years at " . $cities[$station1]["name"]);
$graph->Add($lineplot2);

if ($station2 != "") {
    $lineplot3 = new LinePlot($pct2, $xdata);
    $lineplot3->SetColor("red");
    $lineplot3->SetWeight(3);
    $lineplot3->SetLegend("$yrs2 years at " . $cities[$station2]["name"]);
    $graph->Add($lineplot3);
}


$graph->Stroke();
