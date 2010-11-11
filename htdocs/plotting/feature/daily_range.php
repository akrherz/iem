<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_error.php");
include ("../../../include/jpgraph/jpgraph_plotline.php");
include ("../../../include/jpgraph/jpgraph_line.php");
include ("../../../include/jpgraph/jpgraph_scatter.php");
include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/database.inc.php");

$dates = Array();
$mins = Array();
$avgs = Array();
$maxs = Array();
$errdata = Array();

$fc = file('daily.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $dates[] = strtotime( $tokens[0] );
   $mins[] = $tokens[1];
   $avgs[] = $tokens[2];
   $maxs[] = $tokens[3];
   $errdata[] = floatval($tokens[3]);
   $errdata[] = floatval($tokens[1]);
 }


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"auto");    
$graph->SetScale("datelin");
$graph->legend->Pos(0.05,0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelFormatString("M d", true);
$graph->yaxis->title->Set("Heat Index Temperature [F]");
$graph->title->Set("Des Moines Daily Heat Index Range");
$graph->subtitle->Set("1 July - 15 August 2010");

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,55);

//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Create the error plot
$errplot=new ErrorPlot($errdata, $dates);
$errplot->SetColor("red");
$errplot->SetWeight(2);
$errplot->SetCenter();
$graph->Add($errplot);

$lnplot=new ScatterPlot($avgs, $dates);
$lnplot->SetColor("black");
$lnplot->SetWeight(2);
$lnplot->SetCenter();
$graph->Add($lnplot);


// Display the graph
$graph->Stroke();
?>
