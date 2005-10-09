<?php
include("../../../config/settings.inc.php");
  // 1minute.php

/** Vars */
include_once("$rootpath/include/snet_locs.php");
  include ("$rootpath/include/mlib.php");
  include ("fillholes.inc.php");

$tbl = $cities[strtoupper($tv)][$station];
$station = $tbl["nwn_id"];

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$myTime = strtotime($year."-".$month."-".$day);

$imgwidth = 640;
$imgheight = 480;

$dirRef = strftime("%Y_%m/%d", $myTime);
$matchDate = strftime("%m/%d/%y", $myTime);

$titleDate = strftime("%b %d, %Y", $myTime);
$href = strftime("/tmp/".$station."_%Y_%m_%d", $myTime);

$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min avg Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}


$fcontents = file('/mesonet/ARCHIVE/raw/snet/'.$dirRef.'/'.$station.'.dat');
if (! $fcontents)
{
	echo "<p><b>Error:</b> Archive file does not exist for this date.";
	return;
}

// BUILD Arrays to hold minute-by-minute data
$tmpf = Array(0 => 0);
$dwpf = Array(0 => 0);
$sr = Array(0 => 0);
$mph = array(0 => 0);
$drct = array(0 => 0);
$gust = array(0 => 0);
$prec = array(0 => 0);
$alti = array(0 => 0);


for ($i=1;$i<=1440;$i++)
{
  $tmpf[$i] = "";
  $dwpf[$i] = "";
  $sr[$i] = "";
  $mph[$i] = "";
  $drct[$i] = "";
  $gust[$i] = "";
  $prec[$i] = "";
  $alti[$i] = "";
}


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


$xlabel = Array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_dwpf = 100;
$max_tmpf = 0;
$hasgust = 0;
$peakGust = 0;
$peaksped = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];
  $thisDate = $parts[1];
  if ($thisDate != $matchDate) continue;
  $hhmm = split (":", $thisTime);
  $offset = intval($hhmm[0]) * 60 + intval($hhmm[1]);
  $i = $offset;

  if (substr($parts[6], 0, 2) == "0-"){
    $thisTmpf = intval( substr($parts[6], 1, 2) ) ;
  } else {
    $thisTmpf = intval( substr($parts[6], 0, 3) ) ;
  }
  $thisRelH = intval( substr($parts[7],0,3) );
  $thisSR = intval( substr($parts[4],0,3) ) * 10;
  $thisMPH = intval( substr($parts[3],0,-3) );
  if ($thisMPH > $peaksped) $peaksped = $thisMPH;
  $thisDRCT = $dirTrans[$parts[2]];
  $thisGust = $parts[12];
  if ($thisGust < $peakGust)  $thisGust = $peakGust;
  else $peakGust = $thisGust;
  if (sizeof($parts) > 13) $hasgust = 1;
  $thisALTI = substr($parts[8],0,-1);
  $thisPREC = substr($parts[9],0,-2);


  if ($thisRelH > 0){
    $thisDwpf = dwpf($thisTmpf, $thisRelH);
  } else {
    $thisDwpf = "";
  }
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  } else {
    if ($max_tmpf < $thisTmpf){
      $max_tmpf = $thisTmpf;
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = "";
  }  else {
    if ($min_dwpf > $thisDwpf){
      $min_dwpf = $thisDwpf;
    }
  }

  $shouldbe = intval( $start ) + 60 * $i;
 
  
  $tmpf[$i] = $thisTmpf;
  $dwpf[$i] = $thisDwpf;
  $sr[$i] = $thisSR;
  $xlabel[$i] = $thisTime;
  if ($i % 10 == 0){
    $drct[$i] = $thisDRCT;
  }else{
    $drct[$i] = "-199";
  }
  $mph[$i] = $thisMPH;
  $gust[$i] = $thisGust;
  $prec[$i] = $thisPREC;
  $alti[$i] = $thisALTI * 33.8639;
  if ($alti[$i] < 900)   $alti[$i] = " ";

} // End of while

if ($station >= 900)
{
$tmpf = fillholes($tmpf);
$dwpf = fillholes($dwpf);
$sr = fillholes($sr);
$mph = fillholes($mph);
$drct = fillholes($drct);
$gust = fillholes($gust);
$prec = fillholes($prec);
$alti = fillholes($alti);
}

/* Correct precip */
$r = 0;
for ($i=60;$i<1441;$i++)
{
  if ($prec[$i] < $r){
    $prec[$i] = $r;
  }
  $r = $prec[$i];
}

$xpre = array(0 => '12 AM', '1', '2', '3', '4', '5',
        '6', '7', '8', '9', '10', '11', 'Noon',
        '1', '2', '3', '4', '5', '6', '7',
        '8', '9', '10', '11', 'Mid');

if ($peaksped > $peakGust) $peakGust = $peaksped;

for ($j=0; $j<25; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


// Fix y[0] problems
if ($tmpf[0] == ""){
  $tmpf[0] = 0;
}
if ($dwpf[0] == ""){
  $dwpf[0] = 0;
}
if ($sr[0] == ""){
  $sr[0] = 0;
}

$cityname = $tbl['city'];

include ("/mesonet/php/include/jpgraph/jpgraph.php");
include ("/mesonet/php/include/jpgraph/jpgraph_line.php");
include ("/mesonet/php/include/jpgraph/jpgraph_scatter.php");


function common_graph($graph)
{
  $tcolor = array(230,230,0);
  /* Common for all our plots */
  $graph->img->SetMargin(100,80,80,60);
  //$graph->img->SetAntiAliasing();
  $graph->xaxis->SetTextTickInterval(120);
  $graph->xaxis->SetPos("min");

  $graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,14);
  $graph->xaxis->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->xaxis->title->SetBox( array(150,150,150), $tcolor, true);
  $graph->xaxis->title->SetColor( $tcolor );
  $graph->xaxis->SetTitleMargin(15);

  $graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,14);
  $graph->yaxis->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->yaxis->title->SetBox( array(150,150,150), $tcolor, true);
  $graph->yaxis->title->SetColor( $tcolor );
  $graph->yaxis->SetTitleMargin(50);

  $graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,14);
  $graph->y2axis->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->y2axis->title->SetBox( array(150,150,150), $tcolor, true);
  $graph->y2axis->title->SetColor( $tcolor );
  $graph->y2axis->SetTitleMargin(40);

  $graph->tabtitle->SetFont(FF_ARIAL,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.91, 'left', 'top');
  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

  return $graph;
}

// Create the graph. These two calls are always required
$graph = new Graph($imgwidth,$imgheight,"example1");

$graph->SetScale("textlin", $min_dwpf - 5, $max_tmpf + 5);
$graph->SetY2Scale("lin", 0, 1200);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Solar Radiation [W m**-2]", "low");
$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');
$graph->xaxis->SetTickLabels($xlabel);

$graph = common_graph($graph);

/* Custom */
$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");



$graph->y2axis->scale->ticks->Set(100,25);
$graph->y2axis->scale->ticks->SetLabelFormat("%-4.0f");


// Create the linear plot
$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
//$lineplot->SetWeight(2);
// Create the linear plot

$lineplot2=new LinePlot($dwpf);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
//$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($sr);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");
//$lineplot3->SetWeight(2);

$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke("/mesonet/www/html/".$href."_1.png");

echo '<p><img src="'.$href.'_1.png">';

//__________________________________________________________________________

// Create the graph. These two calls are always required
$graph = new Graph($imgwidth,$imgheight,"example1");

$graph->SetScale("textlin",0, 360);
$graph->SetY2Scale("lin");
$graph->y2axis->SetColor("red");
$graph->y2axis->SetTitle("Wind Speed [MPH]");
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');

$graph = common_graph($graph);

$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->SetColor("blue");
$graph->yaxis->SetTitle("Wind Direction");

// Create the linear plot
$lineplot=new LinePlot($mph);
$lineplot->SetLegend($wLabel);
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
$sp1->SetLegend("Wind Direction");

$graph->Add($sp1);
$graph->AddY2($lineplot);
if ($hasgust == 1){
  $graph->AddY2($lp1);
}

$graph->Stroke("/mesonet/www/html/".$href."_2.png");
echo '<p><img src="'.$href.'_2.png">';

//__________________________________________________________________________

$graph = new Graph($imgwidth,$imgheight);
$graph->SetScale("textlin");
$maxPrec = max($prec);
if ($maxPrec > 3.5)
$graph->SetY2Scale("lin", 0, $maxPrec + 1);
else
$graph->SetY2Scale("lin", 0, 4.00);

$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");
$graph->yaxis->SetTitle("Pressure [millibars]");

$graph = common_graph($graph);

$graph->yaxis->SetTitleMargin(60);

$graph->y2axis->scale->ticks->Set(1,0.25);
$graph->y2axis->scale->ticks->SetLabelFormat("%1.0f");
$graph->y2axis->SetColor("blue");

$graph->yaxis->scale->ticks->SetLabelFormat("%4.1f");
$graph->yaxis->scale->ticks->Set(1,0.1);
$graph->yaxis->SetColor("black");
$graph->yscale->SetGrace(10);
//$graph->yscale->SetAutoTicks();

// Create the linear plot
$lineplot=new LinePlot($alti);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("black");
//$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($prec);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetFillColor("blue@0.1");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);
//$lineplot2->SetFilled();
//$lineplot2->SetFillColor("blue");

// Box for error notations
//$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//$t1->Pos(0.4,0.95);
//$t1->SetOrientation("h");
//$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//$t1->SetColor("black");
//$graph->AddText($t1);

$graph->AddY2($lineplot2);
$graph->Add($lineplot);

$graph->Stroke("/mesonet/www/html/".$href."_3.png");
echo '<p><img src="'.$href.'_3.png">';

?>
