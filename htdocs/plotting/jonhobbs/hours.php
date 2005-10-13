<?php
$connection = pg_connect("localhost","5432","compare");

if ( strlen( $network) == 0  ){
	$network = "asos";
}


$xlen = 24;
$st = 'otm';
$st2 = 'rott';
$stn = 'Ottumwa';

//$data = 'extract(hour from o.valid) as counter';
$data = 't.sknt as counter';
$spec = 'o.valid = t.valid and t.sknt < 25 and t.sknt >= 0';
$group = 'GROUP by counter ORDER by counter ASC';
$var = 'DWPF';
$varname = 'Dew Point';
$groupname = 'Local Hour of the Day';
$xal = 'Local Hour';
//$timeR = "and date(t.valid) >= '2002-02-01' and date(t.valid) < '2002-03-01' ";

//-------------------------------------------------

$query2 = "SELECT avg(o.$var) as oavg, avg(t.$var) as tavg, 
  extract(hour from o.valid) as counter
  from t_$st o, t_$st2 t WHERE o.valid = t.valid and o.$var >= -50 
  and t.$var >= -50 $timeR GROUP by counter ORDER by counter ASC";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

for ($i=0; $i<$xlen; $i++){
  $ydata[$i] = "";
  $ydata2[$i] = "";
}


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $ydata[$row["counter"]]  = $row["oavg"];
  $ydata2[$row["counter"]]  = $row["tavg"];
}

pg_close($connection);


include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");

$goal = Array("awos" => 35, "asos" => 15, "rwis" => 50);

// Create the graph. These two calls are always required
$graph = new Graph(400,300,"example3");
$graph->SetScale("textlin");
$graph->img->SetMargin(50,20,50,40);

//$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);

$graph->yaxis->scale->ticks->Set(1,0.5);
$graph->yaxis->scale->ticks->SetPrecision(1);

$graph->title->Set("2002 RWIS vs ASOS $varname Comparison");
$graph->subtitle->Set("Grouped by $groupname ");
$graph->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->SetTitleMargin(35);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->xaxis->SetTitle($xal);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,10);
//$graph->xaxis->SetTitleMargin(100);
//$graph->xaxis->SetPos("min");
$graph->legend->Pos(0.2, 0.12);
$graph->legend->SetLayout(LEGEND_HOR);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend("$stn ASOS");
$lineplot->SetWeight(3);

$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("$stn RWIS");
$lineplot2->SetWeight(3);

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

