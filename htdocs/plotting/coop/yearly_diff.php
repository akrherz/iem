<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("coop");


$station1 = isset($_GET["station1"]) ? strtolower($_GET["station1"]) : die("No station1");
$station2 = isset($_GET["station2"]) ? strtolower($_GET["station2"]) : die("No station2");
$season = isset($_GET["season"]) ? $_GET["season"]: "";


$months = Array("spring" => "(3, 4, 5)" ,
  "summer" => "(6, 7, 8)",
  "fall" => "(9, 10, 11)",
  "winter" => "(12, 1, 2)");

$labels = Array("spring" => "Spring (MAM)",
  "summer" => "Summer (JJA)",
  "fall" => "Fall (SON)",
  "winter" => "Winter (DJF)" );

$sqlAddition = "";
$sqlAddition2 = "";
if ($season != "all"){
  $sqlAddition = " + '1 month'::timespan ";
  $sqlAddition2 = " and month IN ". $months[$season] ." ";
  $label = $labels[$season];
} else{
  $label = "Yearly";
}


$query2 = "SELECT avg( (high + low) /2 ) as avet, avg(high) as aveh, avg(low) as
 avel, year from alldata WHERE stationid = '". $station1 ."' and high > -90 and low > -90 ". $sqlAddition2 ." GROUP by year ORDER by
 year ASC";
$query3 = "SELECT avg( (high + low) /2 ) as avet, avg(high) as aveh, avg(low) as
 avel, year from alldata WHERE stationid = '". $station2 ."' and high > -90 and low > -90 ". $sqlAddition2 ." GROUP by year ORDER by
 year ASC";


$result = pg_exec($connection, $query2);
$result2 = pg_exec($connection, $query3);

$s1_hi = array();
$s1_av = array();
$s1_lo = array();
$s2_hi = array();
$s2_av = array();
$s2_lo = array();
$xlabel= array();
$years_s1 = 0;
$years_s2 = 0;

for ($i=1893; $i<2001; $i++){
 $s1_hi[$i - 1893] = " ";
 $s1_hi[$i - 1893] = " ";
 $s1_av[$i - 1893] = " ";
 $s1_lo[$i - 1893] = " ";
 $s2_hi[$i - 1893] = " ";
 $s2_av[$i - 1893] = " ";
 $s2_lo[$i - 1893] = " ";
 $xlabel[$i - 1893] = $i; 
}

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $s1_hi[$row["year"] - 1893]  = $row["aveh"];
  $s1_av[$row["year"] - 1893]  = $row["avet"];
  $s1_lo[$row["year"] - 1893]  = $row["avel"];
  $xlabel[$row["year"] - 1893]  = $row["year"];
}

for( $i=0; $row = @pg_fetch_array($result2,$i); $i++)
{
  $s2_hi[$row["year"] - 1893]  = $row["aveh"];
  $s2_av[$row["year"] - 1893]  = $row["avet"];
  $s2_lo[$row["year"] - 1893]  = $row["avel"];
  $xlabel[$row["year"] - 1893]  = $row["year"];
}


pg_close($connection);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;


// Create the graph. These two calls are always required
$graph = new Graph(650,450,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,50);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(5);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($label ." Yearly Averages Comparison");

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yscale->SetGrace(10);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Year");
$graph->xaxis->SetTitleMargin(35);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.06);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($s1_hi);
$lineplot->SetLegend($cities[strtoupper($station1)]["name"] ." Avg High");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($s1_lo);
$lineplot2->SetLegend("Low");
$lineplot2->SetColor("red");

// Create the linear plot
$lineplot3=new LinePlot($s2_hi);
$lineplot3->SetLegend($cities[strtoupper($station2)]["name"] ." Avg High");
$lineplot3->SetColor("blue");

// Create the linear plot
$lineplot4=new LinePlot($s2_lo);
$lineplot4->SetLegend("Low");
$lineplot4->SetColor("blue");

// Create the linear plot
$lineplot5=new LinePlot($s2_av);
$lineplot5->SetLegend("Avg");
$lineplot5->SetColor("blue");

// Create the linear plot
$lineplot6=new LinePlot($s1_av);
$lineplot6->SetLegend("Avg");
$lineplot6->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot6);
$graph->Add($lineplot2);
$graph->Add($lineplot3);
$graph->Add($lineplot5);
$graph->Add($lineplot4);

for ($i=0; $i<11; $i++){
  $graph->AddLine(new PlotLine(VERTICAL,7 + $i*10,"tan",1));
}

// Display the graph
$graph->Stroke();
?>

