<?php
/* Generate a 1 minute plot of temperature, dew point, and solar rad */
require_once "../../../config/settings.inc.php";
include_once("../../../include/network.php");
include_once("../../../include/mlib.php");
include_once("../../../include/database.inc.php");
include("../../../include/jpgraph/jpgraph.php");
include("../../../include/jpgraph/jpgraph_line.php");
include("../../../include/jpgraph/jpgraph_scatter.php");
include("../../../include/jpgraph/jpgraph_date.php");
include("../../../include/jpgraph/jpgraph_led.php");

$nt = new NetworkTable(array("KCCI", "KIMT", "KELO"));
$cities = $nt->table;

$station = isset($_GET["station"]) ? $_GET["station"] : "SKCI4";
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$myTime = mktime(0, 0, 0, $month, $day, $year);
$yesterday = mktime(0, 0, 0, date("m"), date("d"), date("Y")) - 96400;

/* Dig in the archive for our data! */
$dbconn = iemdb("snet");
$tbl = sprintf("t%s", date("Y_m", $myTime));
$stname = uniqid();
pg_prepare($dbconn, $stname, "SELECT * from $tbl 
                 WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");

$rs = pg_execute($dbconn, $stname, array($station, date("Y-m-d", $myTime)));
if (pg_num_rows($rs) == 0) {
    $led = new DigitalLED74();
    $led->StrokeNumber('NO DATA FOR THIS DATE', LEDC_GREEN);
    die();
}

$titleDate = date("M d, Y", $myTime);
$cityname = $cities[$station]['name'];

/* BEGIN GOOD WORK HERE */
$times = array();
$temps = array();
$dewps = array();
$srad  = array();

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $ts = strtotime(substr($row["valid"], 0, 16));
    $times[] = $ts;
    $srad[] = ($row["srad"] >= 0) ? $row["srad"] : "";
    $temps[] = ($row["tmpf"] > -50 && $row["tmpf"] < 120) ? $row["tmpf"] : "";
    $dewps[] = ($row["dwpf"] > -50 && $row["dwpf"] < 120) ? $row["dwpf"] : "";
}

/* Generate Graph Please */
$graph = new Graph(640, 480);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin", 0, 1200);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Solar Radiation [W m**-2]", "low");
$graph->tabtitle->Set(' ' . $cityname . " on " . $titleDate . ' ');

$tcolor = array(230, 230, 0);
/* Common for all our plots */
$graph->img->SetMargin(80, 60, 40, 80);
$graph->xaxis->SetTextTickInterval(120);
$graph->xaxis->SetPos("min");

$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->xaxis->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetTitleMargin(15);
$graph->xaxis->SetLabelFormatString("h A", true);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTitleMargin(50);

$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->yaxis->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->yaxis->SetTitleMargin(50);
$graph->yscale->SetGrace(10);

$graph->y2axis->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->y2axis->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->y2axis->SetTitleMargin(40);

$graph->tabtitle->SetFont(FF_FONT1, FS_BOLD, 16);
$graph->SetColor('wheat');

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.01, 0.94, 'left', 'top');
$graph->legend->SetLineSpacing(3);

$graph->ygrid->SetFill(true, '#EFEFEF@0.5', '#BBCCEE@0.5');
$graph->ygrid->Show();
$graph->xgrid->Show();

$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");

$graph->y2axis->scale->ticks->Set(100, 25);
$graph->y2axis->scale->ticks->SetLabelFormat("%-4.0f");


// Create the linear plot
$lineplot = new LinePlot($temps, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

$lineplot2 = new LinePlot($dewps, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3 = new LinePlot($srad, $times);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");

$graph->Add($lineplot2);
$graph->Add($lineplot);
if ($station != 'SPEI4') {
    $graph->AddY2($lineplot3);
}

$graph->Stroke();
