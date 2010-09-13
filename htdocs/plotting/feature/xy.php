<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$x = Array();
$y = Array();
$xs = Array();
$ys = Array();

$fc = file('xy.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   //$m = floatval($tokens[2]);
   //if ($m == 3 || $m == 4 || $m == 5){
   //  $xs[] = floatval($tokens[1]);
   //  $ys[] = floatval($tokens[0]);
   //} else {
     $x[] = floatval($tokens[1]);
     $y[] = floatval($tokens[2]);
 //  }
 }
$avgT = array_sum($y)/sizeof($y);
$avgR = array_sum($x)/sizeof($x);
$quad = Array(1=>0,2=>0,3=>0,4=>0);
for($i=0;$i<sizeof($x);$i++){
 if ($y[$i] > $avgT && $x[$i] > $avgR){
   $quad[1] += 1;
 } else if ($y[$i] < $avgT && $x[$i] > $avgR){
   $quad[2] += 1;
 } else if ($y[$i] < $avgT && $x[$i] < $avgR){
   $quad[3] += 1;
 } else if ($y[$i] > $avgT && $x[$i] < $avgR){
   $quad[4] += 1;
 }
}
//Array ( [1] => 15 [2] => 35 [3] => 25 [4] => 43 ) 118

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");


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


$graph->yaxis->SetTitle("Maximum Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->xaxis->SetTitle("Month Total Rainfall [inch]");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->title->Set('June for Ames [1893-2009]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.65, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
//$sc1=new ScatterPlot($ys, $xs);
//$sc1->SetLegend("Spring Events");
//$sc1->mark->SetType(MARK_FILLEDCIRCLE);
//$sc1->mark->SetFillColor("green");
//$graph->Add($sc1);

$sc3=new ScatterPlot($y, $x);
//$sc3->SetLegend("Wintertime");
$sc3->mark->SetType(MARK_FILLEDCIRCLE);
$sc3->mark->SetFillColor("blue");
$graph->Add($sc3);

$graph->AddLine(new PlotLine(HORIZONTAL,array_sum($y)/sizeof($y),"red",2));
$graph->AddLine(new PlotLine(VERTICAL,array_sum($x)/sizeof($x),"red",2));

// Display the graph
$graph->Stroke();
?>
