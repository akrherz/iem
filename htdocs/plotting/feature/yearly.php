<?php
include("../../../config/settings.inc.php");


$years = Array();
$svr = Array();
$tor = Array();
$tot = Array();


$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $svr[] = floatval($tokens[1]);
   $tor[] = floatval($tokens[2]);
   $tot[] = floatval($tokens[3]);
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_mgraph.php");

$lm=45;
$rm=5;
// Create the graph. These two calls are always required
$graph = new Graph(640,420,"example1");
$graph->SetScale("textlin",0,100);
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin($lm,$rm,70,39);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(5);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(22);
$graph->yaxis->SetTitleMargin(22);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->xaxis->SetTitle("Year (2010 day thru Jan 25)");
//$graph->yaxis->SetTitle("Number of County Warnings");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set('NWS Warnings for Iowa 1 Jan - 23 Mar');
$graph->subtitle->Set("number of severe t'storm and tornado \ncounty based warnings");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.25,0.3, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($tor);
$lineplot->SetLegend("Tornado");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
//$lineplot->SetAlign("left");
$lineplot->SetFillColor("red");

// Create the linear plot
$lineplot2=new BarPlot($svr);
$lineplot2->SetLegend("Svr T'Storm");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
//$lineplot->SetAlign("left");
$lineplot2->SetFillColor("yellow");

$gp= new AccBarPlot(Array($lineplot, $lineplot2));
$gp->value->Show();
$gp->value->SetFormat('%.0f');
$graph->Add($gp);


//-----------------------------
$graph2 = new Graph(640,210);
$graph2->SetScale('textlin',0,3000);
$graph2->img->SetMargin($lm+5,$rm+10,5,5);
//$graph2->SetMarginColor('white');
$graph2->SetFrame(false);
$graph2->SetBox(true);
$graph2->xgrid->Show();
$graph2->xaxis->SetTickLabels($years);
//$graph2->xaxis->SetTickPositions($tickPositions,$minTickPositions);
//$graph2->xaxis->SetLabelFormatString('My',true);
$graph2->xaxis->SetPos('max');
$graph2->xaxis->HideLabels();
$graph2->xaxis->SetTickSide(SIDE_DOWN);
$graph2->legend->SetPos(0.5,0.1, 'right', 'top');

$sc2=new ScatterPlot($tot);
$sc2->SetLegend("Year Total");
//$sc2->mark->SetType(MARK_X);
//$sc2->mark->SetFillColor("green");
$graph2->Add($sc2);


$mgraph = new MGraph();
$mgraph->SetMargin(2,2,2,2);
$mgraph->SetFrame(true,'darkgray',2);
$mgraph->Add($graph);
$mgraph->Add($graph2,0,420);
$mgraph->Stroke();
?>
