<?php

$stationx = "ALO";
$stationy = "SDA";
$subt = "All Cases";

$connection = pg_connect("localhost","5432", "asos");

$query2 = "select o.dwpf as otmpf, t.dwpf as ttmpf from 
	".$stationx." o, ".$stationy." t 
	WHERE o.valid = t.valid ";
//	and o.sknt > 10";

$result = pg_exec($connection, $query2);

$data_up = array();
$data2_up = array();
$data_down = array();
$data2_down = array();
$eline = array();

$j=0;
$k=0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $otmpf  = $row["otmpf"];
  $ttmpf  = $row["ttmpf"];
  if ($otmpf > $ttmpf){
    $data_up[$j] = $otmpf;
    $data2_up[$j] = $ttmpf;
    $j++;
  } else if ($otmpf < $ttmpf){
    $data_down[$k] = $otmpf;
    $data2_down[$k] = $ttmpf;
    $k++;
  }
}

for( $j=0; $j < 100; $j++){
  $eline[$j] = $j;
}

pg_close($connection);


include ("../dev16/jpgraph.php");
include ("../dev16/jpgraph_line.php");
include ("../dev16/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,550,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($stationx ." vs ".$stationy." 2001 Temperatures");
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
$sp->SetLegend($stationy ." cooler");
$sp->mark->SetWidth(4);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("navy");

// Create the linear plot
$sp2=new ScatterPlot($data2_down, $data_down);
$sp2->SetLegend($stationy ." warmer");
$sp2->mark->SetWidth(4);
$sp2->mark->SetType(MARK_FILLEDCIRCLE);
$sp2->mark->SetFillColor("red");


$l1=new LinePlot($eline);
//$l1->SetSize(2);
$l1->SetColor("red");

// Add the plot to the graph
$graph->Add($sp2);
$graph->Add($sp);
$graph->Add($l1);

// Display the graph
$graph->Stroke();
?>

