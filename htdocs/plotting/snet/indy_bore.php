<?php
// 1 minute schoolnet data plotter
// Cool.....
require_once "../../../config/settings.inc.php";

$fcontents = file("data/SINI4_071002.txt");
$sts = mktime(9,45,0,10,2,2007);
$ets = mktime(12,0,0,10,2,2007);

$mph = array();
$drct = array();
$alti = array();

$dirTrans = array(
  'N' => '360',
 'NNE' => '25',
 'NE' => '45',
 'ENE' => '70',
 'E' => '90',
 'ESE' => '115',
 'SE' => '135',
 'SSE' => '155',
 'S' => '180',
 'SSW' => '205',
 'SW' => '225',
 'WSW' => '250',
 'W' => '270',
 'WNW' => '295',
 'NW' => '305',
 'NNW' => '335');

$i = 0;

$dups = 0;
$missing = 0;
$hasgust = 0;
$peakgust = 0;
$peaksped = 0;
$times = Array();
$lts = 0;

foreach($fcontents as $linenum => $line)
{
  $parts = preg_split ("/,/", $line);
  $thisGust = 0;
  $timestamp = $parts[0];
 
  $thisMPH = intval( substr($parts[6],0,-3) );
  $thisALTI =  substr($parts[11],0,-1);
  $thisDRCT = $dirTrans[$parts[5]];

  if ($lts > 0 && ($timestamp - $lts > 70))
  {
    $times[] = $timestamp + 40;
    $drct[] = "";
    $mph[] = "";
    $alti[] = "";
  }

  if ($timestamp >= $sts && $timestamp < $ets)
  {
    $times[] = $timestamp;
    $drct[] = $thisDRCT;
    $mph[] = $thisMPH;
    $alti[] = $thisALTI;
  }
  $lts = $timestamp;
} // End of while


include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_line.php");
include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/jpgraph/jpgraph_scatter.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale('datlin',0,360);
$graph->SetYScale(0,'lin',0,60);
$graph->SetYScale(1,'lin');
$graph->SetColor("#f0f0f0");
$graph->img->SetMargin(55,110,55,60);

$graph->title->Set("Indianola, Iowa SchoolNet Sub 1 Minute Time Series");
$graph->title->SetFont(FF_FONT1,FS_BOLD,20);

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTitle("Times on the morning of 2 Oct 2007");
$graph->xaxis->SetTitleMargin(27);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelFormatString("h:i", true);
$graph->xaxis->scale->SetTimeAlign(MINADJ_1);
$graph->xaxis->SetLabelAngle(90);


$graph->yaxis->SetFont(FF_FONT1,FS_BOLD, 14);
$graph->yaxis->scale->ticks->Set(45,15);
$graph->yaxis->SetTitle("Wind Direction (blue dots)");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(40);


$graph->ynaxis[0]->SetFont(FF_FONT1,FS_BOLD);
$graph->ynaxis[0]->scale->ticks->Set(10,5);
$graph->ynaxis[0]->SetTitle("Wind Speed [MPH]");
$graph->ynaxis[0]->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->ynaxis[0]->SetTitleMargin(30);
$graph->ynaxis[0]->SetColor("red", "red");
$graph->ynaxis[0]->title->SetColor("red", "red");


//$graph->ynaxis[1]->SetFont(FF_FONT1,FS_BOLD);
//$graph->ynaxis[1]->scale->ticks->Set(0.01,0.005);
$graph->ynaxis[1]->SetTitle("Pressure");
$graph->ynaxis[1]->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->ynaxis[1]->SetTitleMargin(45);
$graph->ynaxis[1]->SetColor("black", "black");
$graph->ynaxis[1]->SetLabelFormat('%0.3f');

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.05);
$graph->legend->SetFont(FF_FONT1,FS_BOLD,14);

// Create the linear plot
$lineplot=new LinePlot($mph, $times);
$lineplot->SetLegend("Instant Wind Speed");
$lineplot->SetColor("red");

$lineplot2=new LinePlot($alti, $times);
$lineplot2->SetLegend("Pressure");
$lineplot2->SetColor("black");

//if ($hasgust == 1){
  // Create the linear plot
//  $lp1=new LinePlot($gust);
//  $lp1->SetLegend("Peak Wind Gust");
//  $lp1->SetColor("black");
//}

// Create the linear plot
$sp1=new ScatterPlot($drct, $times);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
$sp1->SetLegend("Wind Direction");


$graph->Add($sp1);
$graph->AddY(0,$lineplot);
$graph->AddY(1,$lineplot2);
//$graph->AddY2($lp1);
$graph->Stroke();
?>
