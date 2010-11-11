<?php
include("../../../config/settings.inc.php");


$weeks = Array();
$data = Array();


$fc = file('weekly.txt');
$t2000 = mktime(12,0,0,1,1,2000);
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $weeks[] = $t2000 + (floatval($tokens[0]) * 86400.0 * 7.0);
   $data[] = floatval($tokens[1]);
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");

$lm=25;
$rm=5;
// Create the graph. These two calls are always required
$graph = new Graph(320,290,"example1");
$graph->SetScale("datelin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin(45,$rm,30,45);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(5);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(22);
$graph->yaxis->SetTitleMargin(25);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,14);
//$graph->xaxis->SetTitle("Year (2010 day thru Jan 25)");
$graph->yaxis->SetTitle("Days per Year");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set("Days with 2+ inch Rainfall in Iowa");
//$graph->subtitle->Set("measurable precipitation reported");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,16);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.1,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

//$sp = new ScatterPlot($cnt2);
//$sp->SetLegend("Year Total");
//$graph->Add($sp);

// Create the linear plot
$lineplot=new LinePlot($data, $weeks);
//$lineplot->SetLegend("Prior 23 July");
//$lineplot->SetFillGradient('white','darkgreen');
$lineplot->SetStepStyle();
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
