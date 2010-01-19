<?php
include("../../../config/settings.inc.php");


$years = Array();
$cnt = Array();

$ts0 = mktime(0,0,0,1,1,1893);

$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt[] = floatval($tokens[1]);
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(300,280,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,5,65,50);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
$graph->yaxis->SetTitleMargin(20);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->SetTitle("Year");
$graph->yaxis->SetTitle("Minimum Temperature [F]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set('Iowa Minimum November Temperature');
$graph->subtitle->Set('coldest -26 (1898) --- warmest 17 (2009)');

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($cnt);
//$lineplot->SetLegend("When Previous Day < 32");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
$lineplot->SetColor("blue");
$lineplot->SetAlign("left");
$lineplot->SetFillColor("blue");
$graph->Add($lineplot);



// Display the graph
$graph->Stroke();
?>
