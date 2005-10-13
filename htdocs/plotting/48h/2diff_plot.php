<?php
$connection = pg_connect("10.10.10.10","5432","iowa");

if ( strlen($station1) == 3 ) {
	$tableName1 = "azos";

} else{
	$tableName1 = "rwis";
}

if ( strlen($station2) == 3 ) {
        $tableName2 = "azos";

} else{
        $tableName2 = "rwis";
}



$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT (t1.". $data ." - t2.". $data .") as comp1, to_char(t1.valid, 'yymmdd/HH24MI') as 
	ovalid from ". $tableName1 ." t1, ". $tableName2 ." t2  WHERE t1.station = '". $station1 ."' 
	and t2.station = '". $station2 ."' and t1.valid = t2.valid and to_char(t1.valid, 'MI') = '00' 
	and t1.valid + '2 day' > CURRENT_TIMESTAMP and t1.". $data ." > -99 and t2.". $data ." > -99 ORDER by t1.valid DESC LIMIT 48";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);


$ydata = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["comp1"];
  $xlabel[$i] = $row["ovalid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata  = array_reverse( $ydata );
 

pg_close($connection);

$units = "knots";
$ylabel = "Difference [knots]";
if ( $data == "tmpf" || $data == "dwpf"){
	$units = "F";
	$ylabel = "Difference [F]";
}

include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required

$graph = new Graph(550,400,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(60,10,45,110);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set("48 h Difference: ". $station1 ." - ". $station2 );
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.03, 0.05, "right", "top");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->xaxis->SetTitle("Valid Time");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle( $ylabel );
$graph->xaxis->SetTitleMargin(75);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend($data ." Diff ($units)");
$lineplot->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>
