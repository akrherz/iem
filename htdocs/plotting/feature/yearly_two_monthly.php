<?php
include("../../../config/settings.inc.php");


$years = Array();
$data = Array();
$mdata = Array();

$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $data[] = floatval($tokens[1]);
   $years[] = $tokens[0];
 }

$fc = file('yearly2.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $mdata[] = floatval($tokens[1]) / 58.0;
 }


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_mgraph.php");

$lm=45;
$rm=5;
// Create the graph. These two calls are always required
$graph = new Graph(340,220,"example1");
$graph->SetScale("textlin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin($lm,$rm,70,49);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(3);
$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(22);
$graph->yaxis->SetTitleMargin(22);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->SetTitle("Year (2010 day thru Aug 25)");
$graph->yaxis->SetTitle("Days per year");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set('Great Weather Days for Des Moines');
$graph->subtitle->Set("day requires: Dew Point less than 60°F\nPeak wind less than 20 MPH\nScattered cloudiness or clearer\nHigh Temp above average, below in summer");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,16);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.25,0.2, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($data);
//$lineplot->SetLegend("Tornado");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
//$lineplot->SetAlign("left");
$lineplot->SetFillColor("red");

$graph->Add($lineplot);


//-----------------------------
$graph2 = new Graph(340,110);
$graph2->SetScale('textlin');
$graph2->img->SetMargin($lm+5,$rm+10,5,5);
//$graph2->SetMarginColor('white');
$graph2->SetFrame(false);
$graph2->SetBox(true);
$graph2->xgrid->Show();
//$graph2->xaxis->SetTickLabels($years);
//$graph2->xaxis->SetTickPositions($tickPositions,$minTickPositions);
//$graph2->xaxis->SetLabelFormatString('My',true);
//$graph2->xaxis->SetPos('max');
$graph2->yaxis->SetTitle("Days / mo / yr");
$graph2->yaxis->SetTitleMargin(29);
$graph2->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,8);
//$graph2->xaxis->HideLabels();
$graph2->xaxis->SetTickLabels( Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC") );
//$graph2->xaxis->SetTickSide(SIDE_DOWN);
$graph2->legend->SetPos(0.5,0.1, 'right', 'top');

$sc2=new BarPlot($mdata);
//$sc2->SetLegend("Year Total");
//$sc2->mark->SetType(MARK_X);
//$sc2->mark->SetFillColor("green");
$graph2->Add($sc2);


$mgraph = new MGraph();
$mgraph->SetMargin(2,2,2,2);
$mgraph->SetFrame(true,'darkgray',2);
$mgraph->Add($graph);
$mgraph->Add($graph2,0,220);
$mgraph->Stroke();
?>
