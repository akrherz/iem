<?php

$ydata = array();
$xlabel= array();


for($i=11; $i<28;$i++){
  $xlabel[$i-11] = $i;
}

$fcontents = file("airunsum2002.txt");
$i=0;
while (list ($line_num, $line) = each ($fcontents)) {
  $tokens =  preg_split ("/[\s,]+/", $line);

  if ($tokens[0] == $state){
     if ($tokens[1] == $district){
        $ydata[$i] = $tokens[4];
        $i++;
     } 
  } 
}

$dict = Array(
  11 => "Illinios",
  12 => "Indiania",
  13 => "Iowa",
  14 => "Kansas",
  15 => "Minnesota",
  16 => "Missouri",
  17 => "Nebraska",
  18 => "North Dakota",
  19 => "South Dakota",
  20 => "Wisconsin"
);



//---------------------------------

include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example3");
$graph->SetScale("textlin",-20,20);
$graph->img->SetMargin(40,40,50,80);

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetLabelAngle(50);
$graph->xaxis->SetPos("min");

$graph->yaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->ticks->SetPrecision(0);


$graph->title->Set($dict[$state]);
$graph->subtitle->Set("District ".$district);
$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("minusAI");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->xaxis->SetTitle("Climate Week");
//$graph->xaxis->SetTitleMargin(85);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");


// Add the plot to the graph
$graph->Add($lineplot);


// Display the graph
$graph->Stroke();
?>

