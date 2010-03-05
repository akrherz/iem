<?php
include("../../../config/settings.inc.php");

$above = Array();
$below = Array();
$xabove = Array();
$xbelow = Array();

$fc = file('above.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $above[] = floatval($tokens[1]);
   $xabove[] = $tokens[0];
 }

$fc = file('below.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $below[] = floatval($tokens[1]);
   $xbelow[] = $tokens[0];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_log.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("linlin",0,1000);
$graph->img->SetMargin(45,10,35,34);
$graph->SetMarginColor('white');
$graph->SetFrame(false);
//$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
$graph->xaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->ticks->Set(100,50);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(10);
$graph->yaxis->SetTitleMargin(28);

//$graph->yaxis->HideZeroLabel();
$graph->ygrid->SetFill(true,'pink@0.5','skyblue@0.5');
$graph->xgrid->Show();
$graph->ygrid->Show();

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->SetTitle("Temperature Threshold [F]");
$graph->yaxis->SetTitle("Consecuative Days");

$graph->title->Set("Ames [1893-2010] High Temperatures");
//$graph->subtitle->Set("Record stretch of 5+ inch depth\n9 Dec 2009 - current (57 days)");
$graph->title->SetFont(FF_ARIAL,FS_NORMAL,14);
$graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.3,0.1, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new LinePlot($above, $xabove);
$lineplot->SetLegend("Above");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot->SetFillColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($below, $xbelow);
$lineplot2->SetLegend("Below");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot2->SetStepStyle();
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("blue");
$graph->Add($lineplot2);


$graph->AddLine(new PlotLine(HORIZONTAL,365,"gray",2));
$graph->AddLine(new PlotLine(HORIZONTAL,730,"gray",2));

// Display the graph
$graph->Stroke();
?>
