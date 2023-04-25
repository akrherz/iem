<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";
require_once "../../include/jpgraph/jpgraph.php";
require_once "../../include/jpgraph/jpgraph_line.php";
require_once "../../include/jpgraph/jpgraph_date.php";
$nt = new NetworkTable("OT");
$cities = $nt->table;

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$station = isset($_GET["station"]) ? substr(xssafe($_GET["station"]), 0, 10) : "OT0002";

$myTime = mktime(0, 0, 0, $month, $day, $year);

$dirRef = date("Y_m/d", $myTime);
$titleDate = date("M d, Y", $myTime);

$db = iemdb("other");
$rs = pg_prepare($db, "SELECT",  "SELECT * from t{$year} WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");
$rs = pg_execute($db, "SELECT", array($station, date("Y-m-d", $myTime)));

$tmpf = array();
$dwpf = array();
$srad = array();
$times = array();


for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $tmpf[] = $row["tmpf"];
    $dwpf[] = $row["dwpf"];
    $srad[] = $row["srad"];
    $times[] = strtotime($row["valid"]);
} // End of while


// Create the graph. These two calls are always required
$graph = new Graph(600, 300);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin", 0, 1000);

$graph->img->SetMargin(65, 55, 45, 60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(2, 1);
$graph->title->Set("Temperatures & Solar Radiation for " . $cities[$station]['name']);
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.15, 0.11);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);

$graph->yaxis->SetTitle("Temperature [F]");

$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->y2axis->SetTitleMargin(40);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot = new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2 = new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3 = new LinePlot($srad, $times);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");

$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke();
