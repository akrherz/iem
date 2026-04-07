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

$myTime = strtotime($year."-".$month."-".$day);
$titleDate = date("M d, Y", $myTime);

$data = read_data($myTime);

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(75,50,45,80);
$graph->xaxis->SetLabelFormatString("h:i A", true);


$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Temp & RH");
$graph->subtitle->Set($titleDate );

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.11, 0.14);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->SetTitleMargin(40);
$graph->y2axis->SetTitle("Relative Humidity [%]");
$graph->y2axis->SetTitleMargin(40);
$graph->xaxis->SetLabelFormatString("h:i A", true);

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(50);
//$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($data["rh"], $data["times"]);
$graph->AddY2($lineplot);
$lineplot->SetLegend("Outside RH");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($data["tmpf"], $data["times"]);
$graph->Add($lineplot2);
$lineplot2->SetLegend("Air Temperature [F]");
$lineplot2->SetColor("red");

$graph->Stroke();
