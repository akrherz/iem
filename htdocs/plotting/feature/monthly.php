<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$highs = Array(   9,
  14,
  11,
   2,
   9,
  17,
   5,
  24,
  11,
  11,
   3,
   7);
$lows = Array(   9,
  19,
  14,
   6,
  15,
  21,
   9,
  26,
  15,
  15,
  10,
  14);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,480,"example1");
$graph->SetScale("textlin",0,30);

$graph->SetBackgroundGradient('red@0.7','blue@0.7',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,0,25,25);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels( Array("APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT","NOV","DEC","JAN","FEB","MAR") );
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,14);
//$graph->xaxis->SetTitle("* thru September 18th");
//$graph->xaxis->title->SetMargin(20);
//$graph->yaxis->SetTitle('Temp Difference [°F]');
$graph->yaxis->SetTitle('Days Above Average');
$graph->title->Set('Ames days above average per month');
$graph->subtitle->Set('1 Apr 2009 - 23 Mar 2010');
$graph->title->SetFont(FF_ARIAL,FS_BOLD,10);

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.5,0.2, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot( $highs );
$lineplot->SetLegend("High Temp");
$lineplot->SetFillColor("red");
$lineplot->value->Show();
$lineplot->SetValuePos('top');
$lineplot->value->SetFont(FF_ARIAL,FS_BOLD,12);
$lineplot->value->SetColor("black");
$lineplot->value->SetFormat('%.0f');
//$lineplot->SetWidth(1);

// Create the linear plot
$lineplot2=new BarPlot( $lows );
$lineplot2->SetLegend("Low Temp");
$lineplot2->SetFillColor("blue");
$lineplot2->value->Show();
$lineplot2->SetValuePos('top');
$lineplot2->value->SetFont(FF_ARIAL,FS_BOLD,12);
$lineplot2->value->SetFormat('%.0f');
$lineplot2->value->SetColor("black");
//$lineplot->SetWidth(1);

$gp = new GroupBarPlot(Array($lineplot,$lineplot2));
$graph->Add($gp);


// Display the graph
$graph->Stroke();
?>
