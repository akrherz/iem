<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$x = Array();
$y = Array();

$fc = file('scatter.txt');
while (list ($line_num, $line) = each ($fc)) {
   $tokens = split (" ", $line);
   $x[] = floatval($tokens[1]);
   $y[] = floatval($tokens[0]);
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,35,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(14);
$graph->yaxis->SetTitleMargin(30);


$graph->yaxis->SetTitle("Peak Snow Depth [inch]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->xaxis->SetTitle("Days till snow is gone after peak depth");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->title->Set('Ames days to snow gone [1963-2009]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.65, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


$sc3=new ScatterPlot($y, $x);
$sc3->SetLegend("Wintertime");
$sc3->mark->SetType(MARK_FILLEDCIRCLE);
$sc3->mark->SetFillColor("blue");
$graph->Add($sc3);

// Display the graph
$graph->Stroke();
?>
