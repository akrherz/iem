<?php
$connection = pg_connect("10.10.10.40","5432","compare");

if ( strlen($station1) == 3 ) {
	$tableName1 = "transfer";

} else if ( substr($station1,0,1) == "R"){
	$tableName1 = "rtransfer";
} else{
	$tableName1 = "stransfer";
}

if ( strlen($station2) == 3 ) {
        $tableName2 = "transfer";

} else if ( substr($station1,0,1) == "R"){
        $tableName2 = "rtransfer";
} else {
	$tableName2 = "stransfer";
}



$query2 = "SELECT t1.". $data ." as t1_data, t2.". $data ." as t2_data, to_char(t1.valid, 'yymmdd/HH24MI') as 
	ovalid from ". $tableName1 ." t1, ". $tableName2 ." t2  WHERE t1.station = '". $station1 ."' 
	and t2.station = '". $station2 ."' and t1.valid = t2.valid and 
	t1.valid + '1 day' > CURRENT_TIMESTAMP ORDER by t1.valid ASC";


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

pg_close($connection);


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(350,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(30,10,60,100);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextLabelInterval(3);
$graph->xaxis->SetLabelAngle(90);

$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(69);


$graph->title->Set("24 h Comparison for ". $station1 ." & ". $station2);
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend($station1 ." ". $data ." (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend($station2 ." ". $data ." (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

