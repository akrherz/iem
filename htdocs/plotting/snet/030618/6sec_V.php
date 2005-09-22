<?php
// 1 minute schoolnet data plotter
// Cool.....


include ("../../../include/snetLoc.php");

$station = "121";
if (strlen($station) > 3){
    $station = $SconvBack[$station];
} 

$station = intval($station);


if (strlen($year) == 4 && strlen($month) > 0 && strlen(day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime( date("Y-m-d") );
}

$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('../data/030618_121.dat');

$mph = array();
$drct = array();
$gust = array();
$xlabel = array();

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

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$hasgust = 0;
$peakgust = 0;
$peaksped = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[1];
  $thisDate = $parts[2];
  $thisGust = 0;
  if ($thisGust < $peakgust)  $thisGust = $peakGust;
  else $peakgust = $thisGust;
  if (sizeof($parts) > 13) $hasgust = 1;
  $dateTokens = split("/", $thisDate);
  $strDate = "20". $dateTokens[2] ."-". $dateTokens[0] ."-". $dateTokens[1]; 
  $timestamp = strtotime($strDate ." ". $thisTime );
#  echo $thisTime ."||";

  $thisMPH = intval( substr($parts[4],0,-3) );
  if ($thisMPH > $peaksped) $peaksped = $thisMPH;
  $thisDRCT = $dirTrans[$parts[3]];

//  if ($start == 0) {
//    $start = intval($timestamp);
//  } 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
   $drct[$i] = $thisDRCT;
    $mph[$i] = $thisMPH;
    $gust[$i] = $thisGust;
    $xlabel[$i] =  strftime("%I:%M", $timestamp);
    $i++;

} // End of while


if ($peaksped > $peakgust) $peakgust = $peaksped;



include ("../../jpgraph/jpgraph.php");
include ("../../jpgraph/jpgraph_line.php");
include ("../../jpgraph/jpgraph_scatter.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->SetScale("textlin",0, 360);
$graph->SetY2Scale("lin", 0, 60);
$graph->SetColor("#f0f0f0");
$graph->img->SetMargin(55,55,55,60);

$graph->title->Set($Scities[$Sconv[$station]]['city'] ." Time Series");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,20);

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetTitle("Plot between 1 and 2 PM on 18 June 2003");
$graph->xaxis->SetTitleMargin(25);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetPos("min");


$graph->yaxis->SetFont(FF_ARIAL,FS_BOLD, 14);
$graph->yaxis->scale->ticks->Set(45,15);
$graph->yaxis->SetTitle("Wind Direction");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(40);


$graph->y2axis->SetFont(FF_FONT1,FS_BOLD);
$graph->y2axis->scale->ticks->Set(10,5);
$graph->y2axis->SetTitle("Wind Speed [MPH]");
$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(40);
$graph->y2axis->SetColor("red");

$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->Pos(0.05,0.01);
$graph->legend->SetFont(FF_ARIAL,FS_BOLD,14);

// Create the linear plot
$lineplot=new LinePlot($mph);
$lineplot->SetLegend("Instant Wind Speed");
$lineplot->SetColor("red");

if ($hasgust == 1){
  // Create the linear plot
  $lp1=new LinePlot($gust);
  $lp1->SetLegend("Peak Wind Gust");
  $lp1->SetColor("black");
}

// Create the linear plot
$sp1=new ScatterPlot($drct);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);


$graph->Add($sp1);
$graph->AddY2($lineplot);
$graph->AddY2($lp1);
$graph->Stroke();
?>
