<?php
$connection = pg_connect("10.10.10.20","5432","coop");

$months = Array("spring" => "(3, 4, 5)" ,
  "summer" => "(6, 7, 8)",
  "fall" => "(9, 10, 11)",
  "winter" => "(12, 1, 2)");

$labels = Array("spring" => "Spring (MAM)",
  "summer" => "Summer (JJA)",
  "fall" => "Fall (SON)",
  "winter" => "Winter (DJF)" );

if ($season != all){
  $sqlAddition = " + '1 month'::timespan ";
  $sqlAddition2 = " and month IN ". $months[$season] ." ";
  $label = $labels[$season];
} else{
  $label = "Yearly";
}

$query2 = "SELECT avg( (high + low) /2 ) as avet, avg(high) as aveh, avg(low) as avel, year from alldata WHERE stationid = '". $station ."' ". $sqlAddition2 ." GROUP by year ORDER by year ASC";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();
$years = 0;

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["aveh"];
  $ydata2[$i]  = $row["avet"];
  $ydata3[$i]  = $row["avel"];
  $xlabel[$i]  = $row["year"];
}

if (sizeof($ydata) == 51) { // 1951!!
 $offset = 9;
 $decades = 4;
}else if (sizeof($ydata) == 110) { // 1893 !!
 $offset = 7;
 $decades = 10;
}



pg_close($connection);

include ("/mesonet/php/include/jpgraph/jpgraph.php");
include ("/mesonet/php/include/jpgraph/jpgraph_line.php");
include ("../../include/COOPstations.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,70);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(5);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($label ." Average Temps for ". $cities[$station]["city"]);

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Year");
$graph->xaxis->SetTitleMargin(35);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Avg High (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Avg Temp (F)");
$lineplot2->SetColor("green");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetLegend("Avg Low (F)");
$lineplot3->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

for ($i=0; $i < $decades; $i++){
  $graph->AddLine(new PlotLine(VERTICAL, $offset + ($i * 10) ,"tan",1));
}

// Display the graph
$graph->Stroke();
?>

