<?php
include("../../../config/settings.inc.php");


$tmpf = Array();
$freq = Array();

$ts0 = mktime(0,0,0,1,1,1893);

$fc = file('data.txt');
while (list ($line_num, $line) = each ($fc)) {
   $tokens = split (",", $line);
   $tmpf[] = floatval($tokens[0]);
   $freq[] = floatval($tokens[1]) / floatval($tokens[2]) * 100.0;
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("textlin",0,100);
$graph->img->SetMargin(40,5,65,50);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTextTickInterval(3);
$graph->xaxis->SetTickLabels($tmpf);

//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
$graph->yaxis->SetTitleMargin(20);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->SetTitle("Low Temperature [F]");
$graph->yaxis->SetTitle("Frequency [%]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set('Was there snow cover in Ames?');
$graph->subtitle->Set('on first occurance of low temperature');

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($freq);
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
