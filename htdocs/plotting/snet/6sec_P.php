<?php
// 1 minute schoolnet data plotter
// Cool.....


include ("../../include/snetLoc.php");

$station = "68";
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

$fcontents = file('data/030911_68.dat');

$prec = array();
$alti = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;


while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];
  $thisDate = $parts[1];
  $dateTokens = split("/", $thisDate);
  $strDate = "20". $dateTokens[2] ."-". $dateTokens[0] ."-". $dateTokens[1]; 
  $timestamp = strtotime($strDate ." ". $thisTime );
#  echo $thisTime ."||";

  $thisALTI = substr($parts[9],0,-1);
  $thisPREC = substr($parts[10],0,-2);

//  if ($start == 0) {
//    $start = intval($timestamp);
//  } 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
  
  $prec[$i] = $thisPREC;
  $alti[$i] = $thisALTI * 33.8639;
  $xlabel[$i] = substr($parts[1],0,5);
  $i++;
} // End of while

include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->SetScale("textlin", 1012, 1018);
$graph->SetY2Scale("lin", 0, 1.50);
$graph->SetColor("#f0f0f0");

$graph->title->Set($Scities[$Sconv[$station]]['city'] ." Time Series");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,20);
$graph->subtitle->Set($titleDate );

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetTitle("Plot between 2 and 3:30 PM on 11 Sept 2003");
$graph->xaxis->SetTitleMargin(25);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetPos("min");


$graph->yaxis->SetFont(FF_ARIAL,FS_BOLD, 14);
$graph->yaxis->scale->ticks->Set(2,1);
$graph->yaxis->SetTitle("Pressure [mb]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(60);


$graph->y2axis->SetFont(FF_FONT1,FS_BOLD);
$graph->y2axis->scale->ticks->Set(0.50,0.10);
$graph->y2axis->SetTitle("Accumulated Rainfall [inches]");
$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(40);
$graph->y2axis->SetColor("blue");


$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->Pos(0.10,0.10);
$graph->legend->SetFont(FF_ARIAL,FS_BOLD,14);



// Create the linear plot
$lineplot=new LinePlot($alti);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("black");
$lineplot->setWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($prec);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);

$graph->AddY2($lineplot2);
$graph->Add($lineplot);
$graph->Stroke();
?>
