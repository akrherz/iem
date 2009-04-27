<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$coop = iemdb('coop');

$rs = pg_query($coop, "SELECT day, snowd from alldata 
     WHERE stationid = 'ia0200' and day >= '1965-01-01' 
     and day < '2008-01-01' ORDER by day ASC");

$increase = Array();
$nochange = Array();
$decrease = Array();

$dates = Array();
$sts = mktime(12,0,0,11,1,2000);
for($i=0;$i<367;$i++){
 $dates[] = $sts + (86400 * $i);
 $increase[$i] = 0;
 $nochange[$i] = 0;
 $decrease[$i] = 0;
}

$lastv = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $v = $row['snowd'];
  if ($v == 0 && $lastv == 0) continue;
  $doy = intval( date('z', strtotime($row["day"])) );
  if ($lastv > $v) $decrease[$doy] += 1;
  if ($lastv < $v) $increase[$doy] += 1;
  if ($lastv == $v) $nochange[$doy] += 1;
  $lastv = $v;
}
$oct1 = intval( date('z', strtotime('2000-11-01')) );
$apr1 = intval( date('z', strtotime('2000-04-01')) ) - 1;
$decrease = array_merge( array_slice($decrease, $oct1,60),array_slice($decrease, 0, $apr1));
$nochange = array_merge( array_slice($nochange, $oct1,60),array_slice($nochange, 0, $apr1));
$increase = array_merge( array_slice($increase, $oct1,60),array_slice($increase, 0, $apr1));
$dates = array_slice($dates,1,150);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

$graph = new Graph(620,600,"auto");    
$graph->SetScale("datlin",0,42);
$graph->SetShadow();
$graph->img->SetMargin(40,10,40,55);

// Create the linear plots for each category
$dplot[] = new LinePLot($decrease, $dates);
$dplot[] = new LinePLot($nochange, $dates);
$dplot[] = new LinePLot($increase, $dates);

$dplot[0]->SetFillColor("red");
$dplot[0]->SetLegend('Decrease');
$dplot[1]->SetFillColor("blue");
$dplot[1]->SetLegend('No Change');
$dplot[2]->SetFillColor("green");
$dplot[2]->SetLegend('Increase');

// Create the accumulated graph
$accplot = new AccLinePlot($dplot);

// Add the plot to the graph
$graph->Add($accplot);

$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->SetTitle("Number of Years");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.05,0.13);

$graph->title->Set("What happens to the snow pack?");
$graph->subtitle->Set("1965-2007 Ames Data [43 years]");

// Display the graph
$graph->Stroke();
?>
