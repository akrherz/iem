<?php

$stationx = "andy_alo";
$stationy = "andy_dsm";
$subt = "All Cases";

$connection = pg_connect("mesonet","5432", "compare");

$query2 = "select o.dwpf as otmpf, t.dwpf as ttmpf from 
	".$stationx." o, ".$stationy." t 
	WHERE extract(hour from o.valid) = 7
        and o.valid = t.valid ";

$result = pg_exec($connection, $query2);

$data_up = array();
$data2_up = array();
$data_down = array();
$data2_down = array();
$eline = array();

$j=0;
$k=0;
$tdiff = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $otmpf  = $row["otmpf"];
  $ttmpf  = $row["ttmpf"];
  $tdiff = $tdiff + ($otmpf - $ttmpf);
  if ($otmpf > $ttmpf){
    $data_up[$j] = $otmpf;
    $data2_up[$j] = $ttmpf;
    $j++;
  } else {
    $data_down[$k] = $otmpf;
    $data2_down[$k] = $ttmpf;
    $k++;
  }
}

$avgdiff = $tdiff / $i;

for( $j=0; $j < 100; $j++){
  $eline[$j] = $j - $avgdiff;
}

pg_close($connection);


include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");
include ("../dev17/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,550,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($stationx ." vs ".$stationy." 2002 Temperatures");
$graph->subtitle->Set($subt);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle($stationy ." Temp");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle($stationx ." Temp");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(20);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.61, 0.05);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$sp=new ScatterPlot($data2_up, $data_up);
$sp->SetLegend($stationx ." warmer");
$sp->mark->SetWidth(4);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("red");

// Create the linear plot
$sp2=new ScatterPlot($data2_down, $data_down);
$sp2->SetLegend($stationx ." cooler");
$sp2->mark->SetWidth(4);
$sp2->mark->SetType(MARK_FILLEDCIRCLE);
$sp2->mark->SetFillColor("navy");


$l1=new LinePlot($eline);
//$l1->SetSize(2);
$l1->SetColor("red");

// Box for error notations
$t1 = new Text("Avg Diff ". $stationx ."-". $stationy ." : ".round($avgdiff,2) );
$t1->Pos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);


// Add the plot to the graph
$graph->Add($sp2);
$graph->Add($sp);
$graph->Add($l1);

// Display the graph
$graph->Stroke();
?>

