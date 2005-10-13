<?php

if ( strlen($hours) == 0 ){
	$hours = "24";
}

$connection = pg_connect("localhost","5432", "frost");

if ($mode == "diff"){
  $sqlStr = " f.".$param." - s.".$param." as val1, ' ' as val2 "; 
} else {
  $sqlStr = " f.".$param." as val1,  s.".$param." as val2 ";
}

//$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT ".$sqlStr.", 
	to_char(f.valid, 'mmdd/HH24MI') as tvalid 
	from ".$st1." f, ".$st2." s WHERE  s.valid = f.valid and
	date(f.valid) >= '".$date1."' and date(f.valid) <= '".$date2."' 
	ORDER by tvalid ASC";

// $result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["val1"];
  $ydata2[$i]  = $row["val2"];
  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,90);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);

$interval = intval( sizeof($xlabel) / 12 );
if ($interval > 1 ){
//  $graph->xaxis->SetTextLabelInterval($interval);
  $graph->xaxis->SetTextTickInterval($interval);
}
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($st1 ." - ". $st2);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle($param ." Difference");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend($param);
$lineplot->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);

if ($mode == "side"){
  // Create the linear plot
  $lineplot2=new LinePlot($ydata2);
  $lineplot2->SetColor("blue");
  $lineplot2->SetLegend($st2 ." ".$param);

  $graph->Add($lineplot2);
}

// Display the graph
$graph->Stroke();
?>

