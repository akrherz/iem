<?php

if (strlen($year) == 0) $year = 1995;

$connection = pg_connect("iemdb","5432","coop");

$q = "select to_char(valid, 'DDD') as dv, gdd50 from climate WHERE station = 'ia0200' ORDER by dv";

$result = pg_exec($connection, $q);

$r = "select to_char(day, 'DDD') as dv, high, low from alldata 
       WHERE stationid = 'ia0200' and year = $year ORDER by dv";

$r2 = pg_exec($connection, $r);


$ydata = Array();
$rtotal = Array();
$r = 0;
$htotal = Array();
$h = 0;
$diff = Array();

$xlabel = Array();
$xlabel[0] = 90;
$xlabel[30] = 120;
$xlabel[60] = 150;
$xlabel[90] = 180;
$xlabel[120] = 210;
$xlabel[150] = 240;
$xlabel[180] = 270;


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  if ($i > 89 && $i < 271 ){
   $hrow = @pg_fetch_array($r2, $i);
   $high = $hrow["high"];
   $low = $hrow["low"];

   if ($low < 50)  $low = 50.00;
   if ($high > 86) $high = 86.00;
   if ($high < 50) $tgdd = 0.00;
   else $tgdd = (($high+$low)/2.00) - 50.00;
   $h = $h + $tgdd;
   $htotal[$i - 90] = $h;

   $t = $row["gdd50"];
   $r = $r + $t;
   $rtotal[$i - 90] = $r;
   $ydata[$i - 90]  = $row["gdd50"];

   $diff[$i - 90] = $h - $r;
  }
}


include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");

$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin", 0, 3200);
$graph->SetY2Scale("lin", -400, 400);

$graph->img->SetMargin(40,40,80,50);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.10, "right", "top");

$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(30);

$graph->title->Set("Growing Degree Days (50-86)");
$graph->subtitle->Set("Ames, Iowa $year ");


$lineplot=new LinePlot($rtotal);
$lineplot->SetColor("red");
$lineplot->SetLegend("Normal GDD Accum");

$lineplot2=new LinePlot($htotal);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Actual GDD Accum");

$lineplot3=new LinePlot($diff);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("difference");
$lineplot3->SetWeight(3);

$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->AddY2($lineplot3);

$graph->Stroke();

?>
