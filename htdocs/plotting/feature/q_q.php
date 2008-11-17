<?php
include("../../../config/settings.inc.php");

$o1 = Array();
$o2 = Array();
$o3 = Array();
$o4 = Array();
$o5 = Array();
$f1 = Array();
$f2 = Array();
$f3 = Array();
$f4 = Array();
$f5 = Array();


$lines = file("bigtest.txt");
for($i=0; $i < sizeof($lines); $i++)
{
   $vals = explode(',', $lines[$i]);
   $o1[] = $vals[0]; $o2[] = $vals[1]; $o3[] = $vals[2]; $o4[] = $vals[3]; $o5[] = $vals[4];
   $f1[] = $vals[5]; $f2[] = $vals[6]; $f3[] = $vals[7]; $f4[] = $vals[8]; $f5[] = trim($vals[9]);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("lin",0,5);
$graph->img->SetMargin(45,10,5,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);


$graph->yaxis->SetTitle("Predicted Pollen Competition [%]");
$graph->xaxis->SetTitle("Observed Outcrossing [%]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc0=new ScatterPlot($o1, $f1);
$sc0->SetLegend("1.8m R^2=0.005");
$sc0->SetColor("blue");
$graph->Add($sc0);

// Create the linear plot
$sc1=new ScatterPlot($o2, $f2);
$sc1->SetLegend("9.4m R^2=0.003");
$sc1->mark->SetType(MARK_FILLEDCIRCLE);
$sc1->mark->SetFillColor("red");
$graph->Add($sc1);

// Create the linear plot
$sc2=new ScatterPlot($o3, $f3);
$sc2->SetLegend("20.6m R^2=0.004");
$sc2->mark->SetType(MARK_X);
$sc2->mark->SetFillColor("green");
$graph->Add($sc2);

// Create the linear plot
$sc3=new ScatterPlot($o4, $f4);
$sc3->SetLegend("35.8m R^2=0.002");
$sc3->mark->SetType(MARK_CROSS);
$sc3->mark->SetFillColor("lightblue");
$graph->Add($sc3);

// Create the linear plot
$sc4=new ScatterPlot($o5, $f5);
$sc4->SetLegend("200m R^2=0.002");
$sc4->mark->SetType(MARK_DIAMOND);
$sc4->mark->SetFillColor("lightgreen");
$sc4->SetColor("blue");
$graph->Add($sc4);

// Display the graph
$graph->Stroke();
?>
