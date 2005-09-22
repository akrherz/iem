<?php
$connection = pg_connect("localhost","5432","compare");

if ( strlen($station1) == 3 ) {
	$tableName1 = "transfer";

} else{
	$tableName1 = "rtransfer";
}

if ( strlen($station2) == 3 ) {
        $tableName2 = "transfer";

} else{
        $tableName2 = "rtransfer";
}



$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT (t1.tmpf - t2.tmpf) as comp1, (t1.dwpf - t2.dwpf) as comp2, to_char(t1.valid, 'yymmdd/HH24MI') as 
	ovalid from ". $tableName1 ." t1, ". $tableName2 ." t2  WHERE t1.station = '". $station1 ."' 
	and t2.station = '". $station2 ."' and t1.valid = t2.valid and to_char(t1.valid, 'MI') = '00' 
	and t1.valid + '2 day' > CURRENT_TIMESTAMP  ORDER by t1.valid DESC LIMIT 48";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["comp1"];
  $ydata2[$i]  = $row["comp2"];
  $xlabel[$i] = $row["ovalid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata2 = array_reverse( $ydata2 );
  $ydata  = array_reverse( $ydata );
 

pg_close($connection);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,400,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(30,10,60,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set("48 h Difference: ". $station1 ." ASOS - RWIS ");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Temp Diff (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Dewp Diff (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

