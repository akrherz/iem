<?php
$connection = pg_connect("localhost","5432","compare");

$tableName1 = strlen($station1) == 3 ? "transfer" : "rtransfer";
$tableName2 = strlen($station2) == 3 ? "transfer" : "rtransfer";

include("../../include/allLoc.php");

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT t1.". $data ." as t1_data, t2.". $data ." as t2_data, to_char(t1.valid, 'yymmdd/HH24MI') as 
	ovalid from ". $tableName1 ." t1, ". $tableName2 ." t2  WHERE t1.station = '". $station1 ."' 
	and t2.station = '". $station2 ."' and t1.valid = t2.valid and to_char(t1.valid, 'MI') = '00' 
	and t1.valid + '2 day' > CURRENT_TIMESTAMP and t1.". $data ." > -99 and t2.". $data ." > -99 ORDER by t1.valid DESC LIMIT 48";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["t1_data"];
  $ydata2[$i]  = $row["t2_data"];
  $xlabel[$i] = $row["ovalid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata2 = array_reverse( $ydata2 );
  $ydata  = array_reverse( $ydata );
 

pg_close($connection);

$datakey = Array(
  "tmpf" => Array("ytitle" => "Temperature (F)"),
  "dwpf" => Array("ytitle" => "Dew Point (F)"),
  "drct" => Array("ytitle" => "Wind Direction (deg)"),
  "sknt" => Array("ytitle" => "Wind Speed (knots)"),
  "alti" => Array("ytitle" => "Altimeter (inch)")
);

include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(60,10,60,100);
//$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTitle("Valid Time (GMT)");
$graph->yaxis->SetTitle($datakey[$data]['ytitle']);
$graph->xaxis->SetTitleMargin(60);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetPos("min");
$graph->title->Set("48 h Comparison for ". $station1 ." & ". $station2);
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend($cities[$station1]["city"] ." ($station1)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend($cities[$station2]["city"] ." ($station2)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

