<?php
include ("/mesonet/php/include/jpgraph/jpgraph.php");
include ("/mesonet/php/include/jpgraph/jpgraph_line.php");
include ("/mesonet/php/include/jpgraph/jpgraph_date.php");

// Create 100 time/data values "sampled" every 120s
$t = time(); // Get initial timestamp
$datay=array(); $datax=array(); $data2y=array(); $data2x=array();
for($i=0; $i < 1000; ++$i,$t+=120 ) {
    $datay[$i]=rand(30,60);
    $datax[$i]=$t;
    if ($i%2==0){
    $data2y[$i/2]=rand(60,90);
    $data2x[$i/2]=$t+1000;
    }
}

$graph = new Graph(350,200);
$graph->SetMargin(30,10,10,50);
$graph->SetScale("datlin");


// Set the angle for the labels to 90 degrees
$graph->xaxis->SetLabelAngle(90);

$line = new LinePlot($datay,$datax);
$graph->Add($line);

$line2 = new LinePlot($data2y,$data2x);
$graph->Add($line2);
$graph->Stroke();
?>
