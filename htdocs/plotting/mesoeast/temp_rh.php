<?php
include("../../../config/settings.inc.php");
//  1 minute data plotter 

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");


if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mnt/a1/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$rh = array();
$tmpf = Array();
$times = array();

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (" ", $line);
  $month = $parts[0];
  $day = $parts[1];
  $year = $parts[2];
  $hour = $parts[3];
  $min = $parts[4];
  $rh[] = $parts[8];
  $tmpf[] = $parts[5];
  $times[] = mktime($hour,$min,0,$month,$day,$year); 
} // End of while

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(65,40,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
//$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Temp & RH");
$graph->subtitle->Set($titleDate );

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.1,0.01);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Relative Humidity [%]");
$graph->xaxis->SetLabelFormatString("h A", true);

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($rh, $times);
$lineplot->SetLegend("Outside RH");
$lineplot->SetColor("blue");
$graph->AddY2($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($tmpf, $times);
$lineplot2->SetLegend("Air Temperature [F]");
$lineplot2->SetColor("red");
$graph->Add($lineplot2);

$graph->Stroke();

?>
