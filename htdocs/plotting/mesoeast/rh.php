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

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");
$formatFloor = mktime(0, 0, 0, 1, 1, 2016);
$parts = array();
$rhf = array();
$rhi = array();
$times = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 110;
$min_yaxis_i = 110;
$max_yaxis = 0;
$max_yaxis_i = 0;
$prev_Tmpf = 0.0;

foreach($fcontents as $line_num => $line){
	$parts = explode(" ", $line);
	$times[] = strtotime(sprintf("%s %s %s %s %s", $parts[0], $parts[1],
			$parts[2], $parts[3], $parts[4]));
  $thisRhf = $parts[8];
  $thisRhi = intval($parts[18]);
  if ($thisRhf < 0 || $thisRhf > 100 ){
    $thisRhf = "";
  } 
  if ($thisRhi < 0 || $thisRhi > 100 ){
    $thisRhi = "";
  } 


    $rhf[] = $thisRhf;
    $rhi[] = $thisRhi;
 
} // End of while


// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datelin", 0, 100);
$graph->img->SetMargin(65,40,45,60);
$graph->xaxis->SetLabelFormatString("h:i A", true);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Relative Humidity");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Relative Humidity [%]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($rhf, $times);
$lineplot->SetLegend("Outside RH");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($rhi, $times);
$lineplot2->SetLegend("Inside RH");
$lineplot2->SetColor("red");

$graph->Add($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();

?>
