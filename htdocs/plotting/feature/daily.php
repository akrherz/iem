<?php
include("../../../config/settings.inc.php");


$dates = Array();
$cnt = Array();

$fc = file('daily.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt[] = floatval($tokens[1]);
   $dates[] = strtotime($tokens[0]);
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datelin");
$graph->img->SetMargin(40,5,65,50);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
$graph->yaxis->SetTitleMargin(20);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->xaxis->SetTitle("Year");
$graph->yaxis->SetTitle("Frequency [%]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set('White Christmas in Iowa');
$graph->subtitle->Set("frequency of having snowcover \n before and after a White Christmas");

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($cnt, $dates);
//$lineplot->SetLegend("When Previous Day < 32");
//$lineplot->SetFillGradient('white','darkgreen');
$lineplot->SetStepStyle();
$lineplot->SetColor("blue");
//$lineplot->SetAlign("left");
$lineplot->SetFillColor("blue");
$graph->Add($lineplot);



// Display the graph
$graph->Stroke();
?>
