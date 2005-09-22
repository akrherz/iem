<?php
$connection = pg_connect("localhost","5432","asos");
$connection2 = pg_connect("localhost","5432","rwis");

$stime = $year ."-". $month ."-". $day ." ". $shour .":00:00";

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf, to_char(valid, 'yymmdd/HH24MI') as valid from t". $year ." WHERE station = '". $station ."' 
	and valid BETWEEN '". $stime ."' and  ('". $stime ."'::timestamp + '". $duration ." hours'::interval ) ORDER by valid ASC ";

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

$totCount = pg_numrows($result);
$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["tmpf"];
  $ydata2[$i]  = $row["dwpf"];
  if ($i % 3 == 0 && $totCount > 48 ){
  	$xlabel[$j] = $row["valid"];
  	$j++;
  } else {
	$xlabel[$i] = $row["valid"];
  }
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata2 = array_reverse( $ydata2 );
//  $ydata  = array_reverse( $ydata );
 

pg_close($connection);
pg_close($connection2);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,10,20,100);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetPos("min");
if ( $totCount > 48 ){
	$graph->xaxis->SetTextTicks(3);
}
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set( $duration ."h Meteogram for ". $station);

$graph->yaxis->SetTitle("Degree (F)");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.01);

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

