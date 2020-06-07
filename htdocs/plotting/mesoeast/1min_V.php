<?php
require_once "../../../config/settings.inc.php";
// 1 minute schoolnet data plotter
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_scatter.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");


if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime( date("Y-m-d") );
}
$formatFloor = mktime(0, 0, 0, 1, 1, 2016);
$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min Instantaneous Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$mph = array();
$drct = array();
$gust = array();
$xlabel = array();
$times = array();

$start = intval( $myTime );

$dups = 0;
$missing = 0;
$hasgust = 0;
$peakGust = 0;
$peaksped = 0;
$prevMPH = 0;
$prevDRCT = 0;

foreach($fcontents as $line_num => $line){
	$parts = explode(" ", $line);
	$times[] = strtotime(sprintf("%s %s %s %s %s", $parts[0], $parts[1],
			$parts[2], $parts[3], $parts[4]));
  $inTmpf = $parts[5];
  $thisMPH = intval($parts[9]);
  $thisDRCT = intval($parts[10]); 

    if ($line_num % 5 == 0){
      $drct[] = $thisDRCT;
    }else{
      $drct[] = "-199";
    }
    $mph[] = $thisMPH;

} // End of while

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datelin",0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(65,50,55,80);
$graph->xaxis->SetLabelFormatString("h:i A", true);
$graph->xaxis->SetLabelAngle(90);

$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.08);

$graph->yaxis->scale->ticks->Set(90,15);

$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);

$graph->yaxis->SetTitle("Wind Direction");
$graph->y2axis->SetTitle("Wind Speed [MPH]");
$graph->y2axis->SetTitleMargin(40);

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($mph, $times);
$graph->AddY2($lineplot);
$lineplot->SetLegend($wLabel);
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($drct, $times);
$graph->Add($sp1);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

if ($hasgust == 1){
    // Create the linear plot
    $lp1=new LinePlot($gust, $times);
    $graph->AddY2($lp1);
    $lp1->SetLegend("Peak Wind Gust");
    $lp1->SetColor("black");
  }
  

$graph->Stroke();
?>