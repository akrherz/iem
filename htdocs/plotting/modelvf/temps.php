<?php
$connection = pg_connect("localhost","5432","compare");

$station1 = $station;
$tableName1 = "transfer";

$station2 = $station;
$tableName2 = $model . "forecasts";

$data = "tmpf";
$modelrun = $modelrun;
$modelday = $modelday;

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT t1.". $data ." as t1_data, t2.". $data ." as t2_data, to_char(t1.valid, 'yymmdd/HH24MI') as 
	ovalid from ". $tableName1 ." t1, ". $tableName2 ." t2  WHERE t1.station = '". $station1 ."' 
	and t2.station = '". $station2 ."' and t1.valid = t2.valid and to_char(t1.valid, 'MI') = '00' 
	and date_part('hour', t2.modeltime) = ". $modelrun ." and date(t2.modeltime) = '". $modelday ."' and t1.". $data ." > -1 and t2.". $data ." > -1 ORDER by t1.valid DESC LIMIT 48";

#print $query2;

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


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(30,10,60,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("ISU ". $model ." Comparison with Obs for ". $station1 );
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Obs: ". $station1 ." ". $data ." (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("ISU ". $model .": ". $station2 ." ". $data ." (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

