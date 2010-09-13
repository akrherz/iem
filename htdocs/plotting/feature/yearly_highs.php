<?php
include("../../../config/settings.inc.php");


$years = Array();
$vals = Array();

//$ts0 = mktime(0,0,0,1,1,1893);

$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $vals[] = floatval($tokens[1]);
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(45,10,35,65);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(10);
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(33);

//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Number of Days");
$graph->xaxis->SetTitle("*2010 total (8) thru 19 April, climatology 4 days");
//$graph->tabtitle->Set('Ames April Days ');
$graph->title->Set("April Ames days with low\ntemperature 10+ °F warmer than average");

$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
//$graph->xaxis->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->yaxis->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->tabtitle->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($vals);
//$lineplot->SetLegend("When Previous Day < 32");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

$graph->AddLine(new PlotLine(HORIZONTAL,4,"red",2));

// Display the graph
$graph->Stroke();
?>
