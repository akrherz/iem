<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/all_locs.php");
include("$rootpath/include/iemaccess.php");
$iem = new IEMAccess();

/* Get vars */
$station1 = isset($_GET['station1']) ? substr($_GET['station1'],0,10) : "AMW";
$station2 = isset($_GET['station2']) ? substr($_GET['station2'],0,10) : "DSM";
$var = isset($_GET['var']) ? substr($_GET['var'],0,10): 'tmpf';

/* Set up data arrays */
$datay = array($station1 => array(), $station2 => array());
$datax = array($station1 => array(), $station2 => array());

/* Query IEMAccess */
//$sql = "SELECT (extract(EPOCH from CURRENT_TIMESTAMP) - extract(EPOCH from ((CURRENT_TIMESTAMP - '2 days'::interval)::date)::timestamp))::int as toff
$sql = "SELECT extract(EPOCH from valid) as epoch, $var as data, station
  from current_log WHERE station IN ('$station1','$station2') 
  and valid < CURRENT_TIMESTAMP and $var > -99 ORDER by
  valid ASC";
$rs = pg_query($iem->dbconn, $sql);

/* Assign into data arrays */
$cnt=array($station1 => 0, $station2 => 0);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $s = $row["station"];
  $datay[$s][ $cnt[$s] ] = $row["data"];
  $datax[$s][ $cnt[$s] ] = $row["epoch"];
  $cnt[$s] += 1;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,400,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(60,10,60,100);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$titles = Array(
 "tmpf" => "Air Temperature [F]",
 "dwpf" => "Dew Point [F]",
 "sknt" => "Wind Speed [knots]",
 "alti" => "Altimeter [inches]",
 "drct" => "Wind Direction"
);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(60);


$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle($titles[$var]);
$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.06, 'right', 'top');
  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($datay[$station1], $datax[$station1]);
$lineplot->SetLegend($cities[$station1]["city"] ." ($station1)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($datay[$station2], $datax[$station2]);
$lineplot2->SetLegend($cities[$station2]["city"] ." ($station2)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>
