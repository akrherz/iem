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
$formatFloor = mktime(0, 0, 0, 1, 1, 2016);
$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$parts = array();
$tmpf = array();
$times = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 11000;
$min_yaxis_i = 110;
$max_yaxis = 0;
$max_yaxis_i = 0;
$prev_Tmpf = 0.0;

foreach($fcontents as $linenum => $line){
	$parts = explode(" ", $line);
	$times[] = strtotime(sprintf("%s %s %s %s %s", $parts[0], $parts[1],
			$parts[2], $parts[3], $parts[4]));
  $thisTmpf = $parts[13];
  $thisTmpf = round((floatval($thisTmpf) * 33.8639),2);
//  if ($thisTmpf < -50 || $thisTmpf > 150 ){
//  } else {
  if ($max_yaxis < $thisTmpf){
    $max_yaxis = ceil($thisTmpf);
  }
  if ($min_yaxis > $thisTmpf){
    $min_yaxis = floor($thisTmpf);
  }

    $tmpf[] = $thisTmpf;
} // End of while

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datelin");
$graph->img->SetMargin(65,40,45,60);
$graph->xaxis->SetLabelFormatString("h:i A", true);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(1,0.5);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Pressure");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Pressure [mb]");

//[DMF]$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(45);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("red");

$graph->Add($lineplot);

$graph->Stroke();

?>