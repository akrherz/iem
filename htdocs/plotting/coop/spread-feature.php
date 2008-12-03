<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$ts = isset($_GET['ts']) ? strtotime($_GET['ts']) : time();
$dts = strftime("%m%d", $ts);
$plotts = strftime("%d %b", $ts);


$connection = iemdb("coop");

$station = 'ia0600';

//---------------------------------------------------------------

$query2 = "SELECT count(day) as freq, low from alldata 
   WHERE sday = '$dts' and low > -50 and low != high GROUP by low";

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

$query2 = "SELECT count(day) as freq, high from alldata 
   WHERE sday = '$dts' and high > -50 and high != low GROUP by high";

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
  $y1[$i] = @$ydata[$key];
  $y2[$i] = @$ydata2[$key];
  $rh += @floatval($ydata[$key]);
  $rl += @floatval($ydata2[$key]);
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

/* Now, lets compute normal curves! */
function average($array){
    $sum   = array_sum($array);
    $count = count($array);
    return $sum/$count;
}
function deviation ($array, $avg){
    //$avg = average($array);
    foreach ($array as $value) {
        $variance[] = pow($value-$avg, 2);
    }
    $deviation = sqrt(average($variance));
    return $deviation;
}
function normal_sample($x, $avg, $sd){
  $expn = (0 - pow(($x - $avg),2)) / (2.0 * $sd * $sd);
  return 1 / ($sd * sqrt(2 * pi())) * exp($expn);
}

$query3 = "SELECT high, low from alldata 
   WHERE sday = '$dts' and high > -50 and high != low";
$result = pg_exec($connection, $query3);
$highs = Array();
$lows = Array();
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
  $highs[] = $row["high"];
  $lows[] = $row["low"];
}

$h_avg = average($highs);
$cnt = sizeof($highs);
$l_avg = average($lows);
$h_std = deviation($highs, $h_avg);
$l_std = deviation($lows, $l_avg);
$h_norm = Array();
$l_norm = Array();
foreach ($xl as $k => $x){
  //echo "<br>". $x ."--". $h_avg ."--". $h_std ."--". normal_sample($x, $h_avg, $h_std);
  $h_norm[$k] = normal_sample($x, $h_avg, $h_std) * $cnt;
  $l_norm[$k] = normal_sample($x, $l_avg, $l_std) * $cnt;
}

pg_close($connection);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/COOPstations.php");

// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("textlin",0,100);
$graph->SetY2Scale("lin");
$graph->yaxis->scale->ticks->Set(25,5);
$graph->xaxis->scale->ticks->Set(5,1);
$graph->img->SetMargin(60,60,65,50);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xl);
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->scale->SetAutoMax(85);
//$graph->title->Set("Iowa Daily High and Low Temperatures for $plotts");
$graph->title->Set("Iowa Low Temperatures for $plotts");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Cumulative Distribution (percent)");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(35);

$graph->y2axis->SetTitle("Occurances");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(35);

$graph->xaxis->SetTitle("Temperature [F]");
$graph->xaxis->SetTextTickInterval(5);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(15);

$graph->legend->Pos(0.2, 0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$s = sprintf("High Temperature\n  MEAN: %.1f\n  MEDIAN: %.0f\n  STDDEV: %.1f\nLow Temperature\n  MEAN: %.1f\n  MEDIAN: %.0f\n  STDDEV: %.1f\n", $h_avg, $xl[$hm], $h_std, $l_avg, $xl[$lm], $l_std);

$t1 = new Text($s);
$t1->SetPos(75,75);
$t1->SetFont(FF_FONT1,FS_NORMAL);
$t1->SetBox("white","black",true);
$t1->ParagraphAlign("left");
$t1->SetColor("black");
//$graph->AddText($t1);


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

$nl1=new LinePlot($h_norm);
$nl1->SetColor("red@0.7");
$nl1->SetWeight(2);
//$nl1->SetLegend("High Temp");
//$nl1->SetStyle('dashed'); 
//$l1->SetFillColor('red@0.7');
//$l1->SetColor('red@0.8');

$nl2=new LinePlot($l_norm);
$nl2->SetColor("blue@0.7");
$nl2->SetWeight(2);
//$nl2->SetLegend("Low Temp");
//$nl2->SetStyle('dashed'); 
//$l2->SetFillColor('skyblue@0.7');
//$l2->SetColor('navy@0.8');

$lp1=new LinePlot($cy1);
$lp1->SetColor("red");
$lp1->SetLegend("CDF (high temp)");
//$lp1->AddArea($h5,$h95,LP_AREA_NOT_FILLED,"lightred");
//$lp1->AddArea($hm,$hm,LP_AREA_FILLED,"lightred");
$lp1->SetWeight(2);

$lp2=new LinePlot($cy2);
$lp2->SetColor("blue");
$lp2->SetLegend("CDF (low temp)");
//$lp2->AddArea($l5,$l95,LP_AREA_NOT_FILLED,"lightblue");
//$lp2->AddArea($lm,$lm,LP_AREA_FILLED,"lightblue");
$lp2->SetWeight(2);


// Add the plot to the graph
//$graph->Add($gbplot);

//$graph->AddY2($nl1);
$graph->AddY2($nl2);
//$graph->AddY2($l1);
$graph->AddY2($l2);

//$graph->Add($lp1);
$graph->Add($lp2);


// Display the graph
$graph->Stroke();
?>

