<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/jpgraph/jpgraph.php";
require_once "../../include/jpgraph/jpgraph_line.php";
require_once "../../include/jpgraph/jpgraph_date.php";

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$station = substr(get_str404("station", "OT0002"), 0, 10);

$myTime = mktime(0, 0, 0, $month, $day, $year);

$dirRef = date("Y_m/d", $myTime);
$titleDate = date("M d, Y", $myTime);

$db = iemdb("other");
$stname = iem_pg_prepare(
    $db,
    "SELECT * from alldata WHERE station = $1 and valid >= $2 and valid < $3 ORDER by valid ASC",
);
$rs = pg_execute(
    $db,
    $stname,
    array($station, date("Y-m-d", $myTime), date("Y-m-d", $myTime + 86400))
);

$drct = array();
$sknt = array();
$times = array();

while ($row = pg_fetch_assoc($rs)) {
    $sknt[] = $row["sknt"];
    $drct[] = $row["drct"];
    $times[] = strtotime($row["valid"]);
} // End of while


// Create the graph. These two calls are always required
$graph = new Graph(600, 300);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin", 0, 360);

$graph->img->SetMargin(65, 40, 45, 60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(2, 1);
//$graph->yscale->SetGrace(10);
$graph->title->Set("Winds");
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.075);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);

$graph->yaxis->SetTitle("Wind Speed [knots]");

//[DMF]$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetPos("min");

// Create the linear plot
if (sizeof($drct) > 0 && max($drct) > 0) {
    $lineplot = new LinePlot($drct, $times);
    $lineplot->SetLegend("Direction");
    $lineplot->SetColor("blue");
    $graph->AddY2($lineplot);
}

// Create the linear plot
if (sizeof($sknt) > 0 && max($sknt) > 0) {
    $lineplot2 = new LinePlot($sknt, $times);
    $lineplot2->SetLegend("Speed [kts]");
    $lineplot2->SetColor("red");
    $graph->Add($lineplot2);
}

$graph->Stroke();
