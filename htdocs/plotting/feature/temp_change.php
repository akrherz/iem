<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$coop = iemdb('coop');

$rs = pg_query($coop, "SELECT day, high, snowd, low, extract(doy from day) as d 
     from alldata 
     WHERE stationid = 'ia0200' 
     and day < '2008-01-01' and day >= '1908-01-01' and high > -50 ORDER by day ASC");

$increase = Array();
$nochange = Array();
$decrease = Array();

$dates = Array();
$sts = mktime(12,0,0,1,1,2000);
for($i=0;$i<367;$i++){
 $dates[] = $sts + (86400 * $i);
 $increase[$i] = 0;
 $nochange[$i] = 0;
 $decrease[$i] = 0;
}

$lastv = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $v = $row['high'];
  //$doy = intval( date('z', strtotime($row["day"])) );
  $doy = intval( $row["d"]);
  if (($lastv - 5) > $v) $decrease[$doy] += 1;
  else if (($lastv + 5) < $v) $increase[$doy] += 1;
  else $nochange[$doy] += 1;
  $lastv = $v;
}
//print_r($increase);
$oct1 = intval( date('z', strtotime('2000-11-01')) );
$apr1 = intval( date('z', strtotime('2000-04-01')) ) - 1;
//$decrease = array_merge( array_slice($decrease, $oct1,60),array_slice($decrease, 0, $apr1));
//$nochange = array_merge( array_slice($nochange, $oct1,60),array_slice($nochange, 0, $apr1));
//$increase = array_merge( array_slice($increase, $oct1,60),array_slice($increase, 0, $apr1));
//$dates = array_slice($dates,1,150);

$sm_inc = Array();
$sm_dec = Array();
$sm_noc = Array();
for ($i=5;$i<361;$i++){
 $sm_inc[] = array_sum( array_slice($increase,$i-3,11)) / 11.0;
 $sm_noc[] = array_sum( array_slice($nochange,$i-3,11)) / 11.0;
 $sm_dec[] = array_sum( array_slice($decrease,$i-3,11)) / 11.0;
 $sm_dates[] = $dates[$i];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

$graph = new Graph(620,600,"auto");    
$graph->SetScale("datlin",0,100);
$graph->SetShadow();
$graph->img->SetMargin(40,10,40,55);

// Create the linear plots for each category
//$dplot[] = new LinePLot($decrease, $dates);
//$dplot[] = new LinePLot($nochange, $dates);
//$dplot[] = new LinePLot($increase, $dates);
$dplot[] = new LinePLot($sm_dec, $sm_dates);
$dplot[] = new LinePLot($sm_noc, $sm_dates);
$dplot[] = new LinePLot($sm_inc, $sm_dates);

$dplot[0]->SetFillColor("blue");
$dplot[0]->SetLegend('Dec < -5');
$dplot[1]->SetFillColor("green");
$dplot[1]->SetLegend('+/- 5');
$dplot[2]->SetFillColor("red");
$dplot[2]->SetLegend('Inc > +5');

// Create the accumulated graph
$accplot = new AccLinePlot($dplot);

// Add the plot to the graph
$graph->Add($accplot);

$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->SetTitle("Number of Years");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.05,0.09);

$graph->title->Set("High Temp Change Day to Day");
$graph->subtitle->Set("1908-2007 Ames Data [100 years]");

$graph->AddLine(new PlotLine(HORIZONTAL,50,"white",2));
$graph->AddLine(new PlotLine(HORIZONTAL,25,"white",2));
$graph->AddLine(new PlotLine(HORIZONTAL,75,"white",2));



// Display the graph
$graph->Stroke();
?>
