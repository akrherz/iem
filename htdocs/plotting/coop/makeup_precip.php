<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/stats/SimpleLinearRegression.php");
include("$rootpath/include/stats/Histogram.php");

$coop = iemdb("coop");

/* Collect normals for May 1 to TODAY */
$mynorms = Array();
$sql = "SELECT station, sum(precip) as rain from climate51  WHERE
        valid >= '2000-05-01' and valid < '2000-06-24' 
        GROUP by station";
$rs = pg_exec($coop, $sql);
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $mynorms[ $row["station"] ] = $row["rain"];
}

/* Collect normals for May 1 to Oct 1 */
$allnorms = Array();
$sql = "SELECT station, sum(precip) as rain from climate51  WHERE
        valid >= '2000-05-01' and valid < '2000-10-01' 
        GROUP by station";
$rs = pg_exec($coop, $sql);
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $allnorms[ $row["station"] ] = $row["rain"];
}


/* Collect deficits for May 1 to TODAY */
$myobs = Array();
$sql = "SELECT stationid, year, sum(precip) as rain from alldata_ia  WHERE
        extract(doy from day) >= extract(doy from '2000-05-01'::date) and 
        extract(doy from day) < extract(doy from '2000-06-24'::date) and
        year > 1950 and year < 2006 GROUP by stationid, year";
$rs = pg_exec($coop, $sql);
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  if (! array_key_exists($row["stationid"], $myobs)) $myobs[$row["stationid"]] = Array();
  $myobs[ $row["stationid"] ][] = $row["rain"];
}

/* Collect deficits for May 1 to Oct 1 */
$allobs = Array();
$sql = "SELECT stationid, year, sum(precip) as rain from alldata_ia  WHERE
        extract(doy from day) >= extract(doy from '2000-05-01'::date) and 
        extract(doy from day) < extract(doy from '2000-10-01'::date) and
        year > 1950 and year < 2006 GROUP by stationid, year";
$rs = pg_exec($coop, $sql);
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  if (! array_key_exists($row["stationid"], $allobs)) $allobs[$row["stationid"]] = Array();
  $allobs[ $row["stationid"] ][] = $row["rain"];
}

$mydiffs = Array();
$alldiffs = Array();

while( list($stationid, $val) = each($mynorms) )
{
  if (sizeof($myobs[$stationid]) != sizeof($allobs[$stationid])) continue;
  $i = -1;
  while( list($k,$v) = each($myobs[$stationid]) )
  {
    $i += 1;
    $d = $v - $mynorms[$stationid];
    if ($d < -5 or $d > -3) continue;

    $mydiffs[] = $d;
    $alldiffs[] = $allobs[$stationid][$i] - $allnorms[$stationid];
  }
}
//echo sizeof($mydiffs);
//echo sizeof($alldiffs);
$slr = new SimpleLinearRegression($mydiffs, $alldiffs, 95);
$hist = new Histogram($alldiffs, 20);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");

$graph = new Graph(280,200);
$graph->SetScale("lin",0,1);
$graph->img->SetMargin(40,3,50,30);
$graph->title->set("Iowa Rainfall Potential");
$graph->subtitle->set("Assume 3-5 inch May 1 - Jun 24 departure");

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitle("Eventual 1 May - 1 Oct Rainfall Departure");

$graph->yaxis->SetTitle("Probability");

//$graph->title->Set("48 h winds for ". $station);


$sp1 = new ScatterPlot($alldiffs,$mydiffs);


$o = Array(-5,0,5);
$t = Array(-5,0,5);
$o2o = new LinePlot($o, $t);
$o2o->SetWeight(2);
$o2o->SetColor('green');

reset($hist->BINS);
$bvals = Array();
$bweights = Array();
$accum = Array();
$tot = count($alldiffs);
$running = 0;
while (list($k,$v) = each($hist->BINS))
{
   $bweights[] = $v / $tot;
   $bvals[] = $k;
   $accum[] = $running + ($v/$tot);
   $running += ($v/$tot);
}
//print_r($bweights); print_r($bvals); die();

$lplot = new LinePlot($accum, $bvals);
$lplot->SetWeight(2);
$lplot->SetColor('red');

//$lplot->SetLegend('R^2 '. $slr->RSquared);
$bplot = new BarPlot($bweights, $bvals );
$bplot->SetFillColor('orange');
//$bplot->value->Show();
//$bplot->SetAbsWidth(20);
$bplot->SetWidth(1);
$bplot->SetAlign("right"); 
//$bplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAngle(45);
//$bplot->value->SetFormat('%.0d');
$graph->Add($bplot);

//$graph->Add($sp1);
$graph->Add($lplot);
//$graph->Add($o2o);
$graph->Stroke();

?>
