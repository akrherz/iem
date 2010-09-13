<?php
include("../../../config/settings.inc.php");


$years = Array();
$cnt = Array();
$cnt2 = Array();

/*
$fc = file('yearly2.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $cnt2[] = floatval($tokens[1]);
   $years[] = $tokens[0];
 }
*/

$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt[] = floatval($tokens[1]);
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");

$lm=25;
$rm=5;
// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("textlin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin(45,$rm,40,34);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(2);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(22);
$graph->yaxis->SetTitleMargin(28);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,14);
//$graph->xaxis->SetTitle("Year (2010 day thru Jan 25)");
$graph->yaxis->SetTitle("Hours");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set("Hours above 70°F Dew Point");
$graph->subtitle->Set("Des Moines [KDSM]");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,16);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.14, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

//$sp = new ScatterPlot($cnt2);
//$sp->SetLegend("Year Total");
//$graph->Add($sp);

// Create the linear plot
$lineplot=new BarPlot($cnt);
$lineplot->SetLegend("Prior 29 July");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
//$lineplot->SetAlign("left");
$lineplot->SetFillColor("red");

// Create the linear plot
//$lineplot2=new BarPlot($svr);
//$lineplot2->SetLegend("Svr T'Storm");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("yellow");

//$gp= new AccBarPlot(Array($lineplot, $lineplot2));
//$gp->value->Show();
//$gp->value->SetFormat('%.0f');
$graph->Add($lineplot);


$graph->Stroke();
?>
