<?php
$connection = pg_connect("localhost","5432","asos");
$connection2 = pg_connect("localhost","5432","rwis");


$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf, to_char(valid, 'mmdd/HH24MI') as valid from t2002 WHERE station = '". $station ."' 
	and to_char(valid, 'MI') = '00' and valid + '2 day' > CURRENT_TIMESTAMP ORDER by valid DESC LIMIT 48";

if ( strlen($station) == 3 ) {	
	$result = pg_exec($connection, $query1);
	$result = pg_exec($connection, $query2);
} else {
        $result = pg_exec($connection2, $query1);
        $result = pg_exec($connection2, $query2);
}

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["tmpf"];
  $ydata2[$i]  = $row["dwpf"];
  $xlabel[$i] = $row["valid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata2 = array_reverse( $ydata2 );
  $ydata  = array_reverse( $ydata );
 

pg_close($connection);
pg_close($connection2);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,10,45,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set("48 h Meteogram for ". $station);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Dwp (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

