<?php
$connection = pg_connect("10.10.10.10","5432","iowa");

if ( strlen( $network) == 0  ){
	$network = "asos";
}

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT to_char(valid, 'mmdd/HH24MI') as tvalid, count(valid) as tcount from ". $network ." WHERE (valid + '48 hours'::interval) > CURRENT_TIMESTAMP GROUP by tvalid ORDER by tvalid";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$xlabel= array();


$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{

//  echo ":". $row["tcount"] .":";  
  $ydata[$i]  = $row["tcount"];


  if ( $i % 3 == 0 && $network != "asos") {
	$xlabel[$j] = $row["tvalid"];
	$j = $j +1 ;
  } elseif ($network == "asos") {
	$xlabel[$i] = $row["tvalid"];
  }
//  echo ":". $xlabel[$i] .":";
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata2 = array_reverse( $ydata2 );
//  $ydata  = array_reverse( $ydata );
 

pg_close($connection);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

$goal = Array("awos" => 35, "asos" => 15, "rwis" => 50);

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example3");
$graph->SetScale("textlin",0,50);
$graph->img->SetMargin(40,20,50,100);

//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);

$graph->yaxis->scale->ticks->Set(5,1);
$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->Set("Total $network observations per valid time");
//$graph->subtitle->Set("Total Possible: ". $goal[$network] );
$graph->title->SetFont(FF_VERDANA,FS_BOLD,16);
$graph->yaxis->SetTitle("Total Valid Obs");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid GMT Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);


if ($network != "asos") {
	$graph->xaxis->SetTextTicks(3);
}

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>

