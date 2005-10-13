<?php

$stationx = "ALO";
$stationy = "SDA";
$subt = "All Cases";

$connection = pg_connect("localhost","5432", "asos");

$query2 = "select extract(month from o.valid) as month, o.dwpf as otmpf, t.dwpf as ttmpf from 
	".$stationx." o, ".$stationy." t 
	WHERE o.valid = t.valid ";
//	and o.sknt > 10";

$result = pg_exec($connection, $query2);

$jun_data1 = array();
$jun_data2 = array();
$jul_data1 = array();
$jul_data2 = array();
$aug_data1 = array();
$aug_data2 = array();
$sep_data1 = array();
$sep_data2 = array();
$oct_data1 = array();
$oct_data2 = array();
$nov_data1 = array();
$nov_data2 = array();
$dec_data1 = array();
$dec_data2 = array();
$eline = array();

$jun=0;
$jul=0;
$aug=0;
$sep=0;
$oct=0;
$nov=0;
$dec=0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $otmpf  = $row["otmpf"];
  $ttmpf  = $row["ttmpf"];
  $month = $row["month"];
  if ($month == 6){
    $jun_data1[$jun] = $otmpf;
    $jun_data2[$jun] = $ttmpf;
    $jun++;
  } else if ($month == 7){
    $jul_data1[$jul] = $otmpf;
    $jul_data2[$jul] = $ttmpf;
    $jul++;
  } else if ($month == 8){
    $aug_data1[$aug] = $otmpf;
    $aug_data2[$aug] = $ttmpf;
    $aug++;
  } else if ($month == 9){
    $sep_data1[$sep] = $otmpf;
    $sep_data2[$sep] = $ttmpf;
    $sep++;
  } else if ($month == 10){
    $oct_data1[$oct] = $otmpf;
    $oct_data2[$oct] = $ttmpf;
    $oct++;
  } else if ($month == 11){
    $nov_data1[$nov] = $otmpf;
    $nov_data2[$nov] = $ttmpf;
    $nov++;
  } else if ($month == 12){
    $dec_data1[$dec] = $otmpf;
    $dec_data2[$dec] = $ttmpf;
    $dec++;
  } 
}


for( $j=0; $j < 100; $j++){
  $eline[$j] = $j;
}

pg_close($connection);


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");
include ("../dev15/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(300,250,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($stationx ." vs ".$stationy." 2001 Dew Points");
$graph->subtitle->Set($subt);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle($stationy ." Dewp");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle($stationx ." Dewp");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(20);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.6, 0.1);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$sp=new ScatterPlot($jun_data2, $jun_data1);
$sp->SetLegend("June");
$sp->mark->SetWidth(4);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("navy");

// Create the linear plot
$sp2=new ScatterPlot($jul_data2, $jul_data1);
$sp2->SetLegend("July");
$sp2->mark->SetWidth(4);
$sp2->mark->SetType(MARK_FILLEDCIRCLE);
$sp2->mark->SetFillColor("red");

// Create the linear plot
$sp3=new ScatterPlot($aug_data2, $aug_data1);
$sp3->SetLegend("August");
$sp3->mark->SetWidth(4);
$sp3->mark->SetType(MARK_FILLEDCIRCLE);
$sp3->mark->SetFillColor("green");

// Create the linear plot
$sp4=new ScatterPlot($sep_data2, $sep_data1);
$sp4->SetLegend("September");
$sp4->mark->SetWidth(4);
$sp4->mark->SetType(MARK_FILLEDCIRCLE);
$sp4->mark->SetFillColor("yellow");

// Create the linear plot
$sp5=new ScatterPlot($oct_data2, $oct_data1);
$sp5->SetLegend("October");
$sp5->mark->SetWidth(4);
$sp5->mark->SetType(MARK_FILLEDCIRCLE);
$sp5->mark->SetFillColor("pink");

// Create the linear plot
$sp6=new ScatterPlot($nov_data2, $nov_data1);
$sp6->SetLegend("November");
$sp6->mark->SetWidth(4);
$sp6->mark->SetType(MARK_FILLEDCIRCLE);
$sp6->mark->SetFillColor("brown");

// Create the linear plot
$sp7=new ScatterPlot($dec_data2, $dec_data1);
$sp7->SetLegend("December");
$sp7->mark->SetWidth(4);
$sp7->mark->SetType(MARK_FILLEDCIRCLE);
$sp7->mark->SetFillColor("teal");


$l1=new LinePlot($eline);
//$l1->SetSize(2);
$l1->SetColor("red");


// Add the plot to the graph
//$graph->Add($sp);
//$graph->Add($sp2);
//$graph->Add($sp3);
//$graph->Add($sp4);
//$graph->Add($sp5);
$graph->Add($sp6);
//$graph->Add($sp7);
$graph->Add($l1);

// Display the graph
$graph->Stroke();
?>

