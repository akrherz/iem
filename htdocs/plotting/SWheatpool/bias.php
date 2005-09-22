<?php
$connection = pg_connect("localhost","5432","compare");

if ( strlen( $network) == 0  ){
	$network = "asos";
}


$xlen = 25;
//$data = 'extract(hour from o.valid) as counter';
$data = 't.sknt as counter';
$spec = 'o.valid = t.valid and t.sknt < 25 and t.sknt >= 0';
$group = 'GROUP by counter ORDER by counter ASC';
$var = 'TMPF';
$varname = 'Temperature';
$groupname = 'RWIS Wind Speed | Constraint < 25 knots';
$xal = 'RWIS Wind Speed [knots]';

//-------------------------------------------------
$st1 = 'andy_alo';
$st12 = 'andy_dsm';
$nst1 = 'Davenport';
//-_-_-_-_
$st2 = 'sux';
$st22 = 'rsio';
$nst2 = 'Sioux City';
//-_-_-_-_
$st3 = 'alo';
$st32 = 'rwat';
$nst3 = 'Waterloo';
//=================================================

$query2 = "select $data , avg(t.$var - o.$var) as diff
  from $st1 o, $st12 t WHERE $spec
  $group ";
$query3 = "select $data , avg(t.$var - o.$var) as diff
  from t_$st2 o, t_$st22 t WHERE $spec
  $group ";

$query4 = "select $data , avg(t.$var - o.$var) as diff
  from t_$st3 o, t_$st32 t WHERE $spec
  $group ";


$result = pg_exec($connection, $query2);
$result2 = pg_exec($connection, $query3);
$result3 = pg_exec($connection, $query4);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();

for ($i=0; $i<$xlen; $i++){
  $ydata[$i] = "";
  $ydata2[$i] = "";
  $ydata3[$i] = "";
}


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $ydata[$row["counter"]]  = $row["diff"];
}
for( $i=0; $row = @pg_fetch_array($result2,$i); $i++) 
{
  $ydata2[$row["counter"]]  = $row["diff"];
}
for( $i=0; $row = @pg_fetch_array($result3,$i); $i++) 
{
  $ydata3[$row["counter"]]  = $row["diff"];
}


pg_close($connection);


include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");

$goal = Array("awos" => 35, "asos" => 15, "rwis" => 50);

// Create the graph. These two calls are always required
$graph = new Graph(400,300,"example3");
$graph->SetScale("textlin", -5, 5);
$graph->img->SetMargin(50,20,50,30);

//$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);

$graph->yaxis->scale->ticks->Set(1,0.5);
$graph->yaxis->scale->ticks->SetPrecision(1);

$graph->title->Set("RWIS vs ASOS $varname Comparison");
$graph->subtitle->Set("Grouped by $groupname ");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,10);
$graph->yaxis->SetTitle("RWIS $var - ASOS $var");
$graph->yaxis->SetTitleMargin(35);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetTitle($xal);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetTitleMargin(100);
//$graph->xaxis->SetPos("min");
$graph->legend->Pos(0.2, 0.12);
$graph->legend->SetLayout(LEGEND_HOR);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend($nst1);
$lineplot->SetWeight(3);

$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend($nst2);
$lineplot2->SetWeight(3);

$lineplot3=new LinePlot($ydata3);
$lineplot3->SetColor("green");
$lineplot3->SetLegend($nst3);
$lineplot3->SetWeight(3);

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

// Display the graph
$graph->Stroke();
?>

