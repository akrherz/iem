<?php
// 1 minute schoolnet data plotter
// Cool.....
include("../../../config/settings.inc.php");

$myTime
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('data/SWAI4_090226.txt');

$tmpf = array();
$dwpf = array();
$sr = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 100;
$max_yaxis = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[1];
  $thisDate = $parts[2];
  $dateTokens = split("/", $thisDate);
  $strDate = "20". $dateTokens[2] ."-". $dateTokens[0] ."-". $dateTokens[1]; 
  $timestamp = strtotime($strDate ." ". $thisTime );
  
  $thisTmpf = intval( substr($parts[7],0,3) );
  $thisRelH = intval( substr($parts[8],0,3) );
  $thisSR = intval( substr($parts[5],0,3) ) * 10;
  $thisTmpk = 273.15 + (5.00/9.00 * ($thisTmpf - 32.00 ));
  $thisDwpk = $thisTmpk / (1+ 0.000425 * $thisTmpk * -(log10($thisRelH/100.00)));
  $thisDwpf = intval( ( $thisDwpk - 273.15 ) * 9.00/5.00 + 32 );
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = " ";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = $thisTmpf;
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = " ";
  }  else {
    if ($min_yaxis > $thisDwpf){
      $min_yaxis = $thisDwpf;
    }
  }

 
    $tmpf[$i] = $thisTmpf;
    $dwpf[$i] = $thisDwpf;
    $sr[$i] = $thisSR;
    $xlabel[$i] = strftime("%I:%M", $timestamp);
    $i++;

} // End of while


include ("$rootpath/jpgraph/jpgraph.php");
include ("$rootpath/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->img->SetMargin(55,55,55,60);
$graph->SetScale("textlin", 55, 85);
$graph->SetY2Scale("lin", 0, 2000);
$graph->SetColor("#f0f0f0");

$graph->title->Set(" Time Series");
$graph->title->SetFont(FF_FONT1,FS_BOLD,20);
$graph->subtitle->Set("AAA");

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetTitle("Plot between 2 and 3:30 PM on 11 Sept 2003");
$graph->xaxis->SetTitleMargin(25);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");


$graph->yaxis->SetFont(FF_FONT1,FS_BOLD, 14);
$graph->yaxis->SetColor("red");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(35);


$graph->y2axis->SetFont(FF_FONT1,FS_BOLD);
$graph->y2axis->scale->ticks->Set(250,100);
$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(40);


$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->Pos(0.15,0.15);
$graph->legend->SetFont(FF_FONT1,FS_BOLD,14);

// Create the linear plot
$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($dwpf);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($sr);
$lineplot3->SetLegend("Solar Radiation");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(1);


$graph->AddY2($lineplot3);
$graph->Add($lineplot);
$graph->Add($lineplot2);

$graph->Stroke();

?>
