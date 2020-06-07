<?php
require_once "../../../config/settings.inc.php";
//  1 minute data plotter 
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");


if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}
$formatFloor = mktime(0, 0, 0, 1, 1, 2016);
$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$rh = array();
$tmpf = Array();
$times = array();

foreach($fcontents as $line_num => $line){
	$parts = explode(" ", $line);
	$times[] = strtotime(sprintf("%s %s %s %s %s", $parts[0], $parts[1],
			$parts[2], $parts[3], $parts[4]));
  $rh[] = $parts[8];
  $tmpf[] = $parts[5];
} // End of while


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
$lineplot=new LinePlot($rh, $times);
$graph->AddY2($lineplot);
$lineplot->SetLegend("Outside RH");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($tmpf, $times);
$graph->Add($lineplot2);
$lineplot2->SetLegend("Air Temperature [F]");
$lineplot2->SetColor("red");

$graph->Stroke();

?>