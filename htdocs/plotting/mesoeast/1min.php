<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/mesoeast.php";

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));

$myTime = mktime(0, 0, 0, $month, $day, $year);

$titleDate = date("M d, Y", $myTime);

$data = read_data($myTime);


// Create the graph. These two calls are always required
$graph = new Graph(600, 300, "example1");
$graph->SetScale("datelin");

$graph->img->SetMargin(65, 40, 45, 80);
$graph->xaxis->SetLabelFormatString("h:i A", true);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Outside Temperatures");
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.075);


$graph->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot = new LinePlot($data['tmpf'], $data['times']);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2 = new LinePlot($data['dwpf'], $data['times']);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

$graph->Add($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();
