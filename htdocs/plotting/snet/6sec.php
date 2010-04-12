<?php
// 1 minute schoolnet data plotter
// Cool.....
include("../../../config/settings.inc.php");

$myTime = mktime(18,0,0,4,6,2010);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('data/SWII4_100406.txt');

$tmpf = array();
$dwpf = array();
$sr = array();
$times = array();
$drct = Array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 100;
$max_yaxis = 0;

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


while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $times[] = floatval($parts[0]);
  $thisTime = $parts[3];
  $thisDate = $parts[4];
  $dateTokens = split("/", $thisDate);
  $strDate = "20". $dateTokens[2] ."-". $dateTokens[0] ."-". $dateTokens[1]; 
  $timestamp = strtotime($strDate ." ". $thisTime );
  $drct[] = $dirTrans[$parts[5]]; 
 
  $thisTmpf = intval( substr($parts[9],0,3) );
  $thisRelH = intval( substr($parts[10],0,3) );
  $thisSR = intval( substr($parts[7],0,3) ) * 10;
  $thisTmpk = 273.15 + (5.00/9.00 * ($thisTmpf - 32.00 ));
  $thisDwpk = $thisTmpk / (1+ 0.000425 * $thisTmpk * -(log10($thisRelH/100.00)));
  $thisDwpf = intval( ( $thisDwpk - 273.15 ) * 9.00/5.00 + 32 );
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = $thisTmpf;
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = "";
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


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->img->SetMargin(55,55,55,60);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin", 0, 360);
$graph->SetColor("#f0f0f0");

$graph->title->Set(" Time Series");
$graph->title->SetFont(FF_FONT1,FS_BOLD,20);
$graph->subtitle->Set("AAA");

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextTickInterval(60);
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
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new ScatterPlot($drct, $times);
$lineplot3->SetLegend("Solar Radiation");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(1);


$graph->AddY2($lineplot3);
$graph->Add($lineplot);
$graph->Add($lineplot2);

$graph->Stroke();

?>
