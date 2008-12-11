<?php
$ts = "(6)";
$plotts = "June";

$connection = pg_connect("iemdb","5432","coop");
//---------------------------------------------------------------
$total = floatval((51 * 100) + (3 * 184)) * 1.0;

$query2 = "SELECT count(day) / $total.0  as freq, low from alldata 
   WHERE month IN $ts and year > 1950 and low > -50 and low != high GROUP by low";
$result = pg_exec($connection, $query2);

$ydata2 = array();
$lo_cdf = array();

$row0 = @pg_fetch_array($result,0);
$lowV = $row0["low"];

$lowV = 100;

$low_tot = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $low_tot += floatval($row["freq"]);
  $ydata2[intval($row["low"])]  = $row["freq"];
  $lowV = (intval($row["low"]) < $lowV) ? intval($row["low"]) : $lowV;
}

//----------------------------------------------------------------

$query2 = "SELECT count(day) / $total.0 as freq, high from alldata 
   WHERE month IN $ts and year > 1950 and high > -50 and high != low GROUP by high";

$result = pg_exec($connection, $query2);

$ydata = array();
$hi_cdf = array();
$years = 0;

$row0 = @pg_fetch_array($result,0);

$highV = 0;

$hi_tot = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $hi_tot += floatval($row["freq"]);
  $ydata[intval($row["high"])]  = $row["freq"];
  $highV = (intval($row["high"]) > $highV) ? intval($row["high"]) : $highV;
}

$xlabel = Array();
if (intval($lowV) < 0) {
  $low5 = intval($lowV) - (5 + (intval($lowV) % 5));
} else  {
  $low5 = $lowV - ($lowV % 5);
}
$high5 = $highV - ($highV % 5) + 5;

for ($i = $low5; $i <= $high5; $i++){
  $xlabel[$i] = $i;
}


$xl = array();
$y1 = array();
$y2 = array();
$cy1 = array();
$cy2 = array();

$i=0;
$rh=0;
$rl=0;
$h5=-99; $l5 = -99;
$h95=-99; $l95 = -99;
$hm=-99;$lm=-99;
foreach ($xlabel as $key => $value){
  $xl[$i] = $value;
  $y1[$i] = $ydata[$key];
  $y2[$i] = $ydata2[$key];
  $rh += floatval($ydata[$key]);
  $rl += floatval($ydata2[$key]);
  $cy1[$i] = $rh / $hi_tot * 100.0;
  if ($cy1[$i] >= 5 && $h5 == -99) $h5 = $i;
  if ($cy1[$i] >= 50 && $hm == -99) $hm = $i;
  if ($cy1[$i] >= 95 && $h95 == -99) $h95 = $i;
  $cy2[$i] = $rl / $low_tot * 100.0;
  if ($cy2[$i] >= 5 && $l5 == -99) $l5 = $i;
  if ($cy2[$i] >= 50 && $lm == -99) $lm = $i;
  if ($cy2[$i] >= 95 && $l95 == -99) $l95 = $i;
  $i++;
} 

pg_close($connection);

include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_bar.php");
include ("../jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(800,480,"example1");
$graph->SetScale("textlin",0,100);
$graph->SetY2Scale("lin");
$graph->yaxis->scale->ticks->Set(25,5);
$graph->xaxis->scale->ticks->Set(5,1);
$graph->img->SetMargin(60,60,65,50);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xl);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Daily High and Low Temperatures for $plotts");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Cumulative Distribution (percent)");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(35);

$graph->y2axis->SetTitle("Days per month");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(35);

$graph->xaxis->SetTitle("Temperature [F]");
$graph->xaxis->SetTextTickInterval(5);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(15);

$graph->legend->Pos(0.2, 0.09);
$graph->legend->SetLayout(LEGEND_HOR);

/*
// Create the linear plot
$bp0=new BarPlot($y1);
$bp0->SetFillColor("red");
$bp0->SetLegend("High Temp (F)");

// Create the linear plot
$bp1=new BarPlot($y2);
$bp1->SetFillColor("blue");
$bp1->SetLegend("Low Temp (F)");

$gbplot = new GroupBarPlot(array($bp0,$bp1));
$gbplot->SetWidth(0.9);
*/

$l1=new LinePlot($y1);
$l1->SetColor("red");
$l1->SetWeight(2);
$l1->SetLegend("High Temp");
$l1->SetStyle('dashed'); 

$l2=new LinePlot($y2);
$l2->SetColor("blue");
$l2->SetWeight(2);
$l2->SetLegend("Low Temp");
$l2->SetStyle('dashed'); 



$lp1=new LinePlot($cy1);
$lp1->SetColor("red");
$lp1->SetLegend("CDF (high temp)");
$lp1->AddArea($h5,$h95,LP_AREA_NOT_FILLED,"lightred");
$lp1->AddArea($hm,$hm,LP_AREA_FILLED,"lightred");
$lp1->SetWeight(2);

$lp2=new LinePlot($cy2);
$lp2->SetColor("blue");
$lp2->SetLegend("CDF (low temp)");
$lp2->AddArea($l5,$l95,LP_AREA_NOT_FILLED,"lightblue");
$lp2->AddArea($lm,$lm,LP_AREA_FILLED,"lightblue");
$lp2->SetWeight(2);


// Add the plot to the graph
//$graph->Add($gbplot);

$graph->AddY2($l1);
$graph->AddY2($l2);

$graph->Add($lp1);
$graph->Add($lp2);


// Display the graph
$graph->Stroke();
?>
