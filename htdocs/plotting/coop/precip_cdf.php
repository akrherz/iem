<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

function standard_deviation($std) 
     {
     $total = 0;$sum=0;
     while(list($key,$val)=each($std))
          {
          $total += $val;
          }
     reset($std);
     $mean = $total/count($std);
     while(list($key,$val) = each($std))
          {
          $sum += pow(($val-$mean),2);
          }
     $var = sqrt($sum/(count($std)-1));
     return round($var,2); 
     } 

$station = isset($_GET["station"]) ? strtolower($_GET['station']): 'ia0200';
/* Setup start/end dates */
$smonth = isset($_GET['smonth']) ? $_GET['smonth'] : 5;
$sday = isset($_GET['sday']) ? $_GET['sday'] : 1;
$emonth = isset($_GET['emonth']) ? $_GET['emonth'] : 5;
$eday = isset($_GET['eday']) ? $_GET['eday'] : 31;
$sts = mktime(0,0,0,$smonth,$sday,2000);
$ets = mktime(0,0,0,$emonth,$eday,2000);
$stsSQL = date("Y-m-d", $sts);
$etsSQL = date("Y-m-d", $ets);
$subtitle = sprintf("Between %s and %s", date('M d', $sts), date('M d', $ets));

/* Query out the average accumulations during that time */
$coop = iemdb("coop");
$sql = "select year, round(sum(precip)::numeric,2) as rain from alldata WHERE extract(doy from day) BETWEEN extract(doy from '$stsSQL'::date) and extract(doy from '$etsSQL'::date) and stationid = '$station' and year < extract(year from now()) GROUP by year ORDER by rain ASC";
$rs = pg_exec($coop, $sql);

/* Generate plot */
$rowcount = pg_numrows($rs);
$data = Array();
$rdata = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  if($i==0){$lowVal = $row["rain"]; $lowYear = $row["year"];}
  if($i==$rowcount-1){$hiVal = $row["rain"]; $hiYear = $row["year"];}

  if (array_key_exists($row["rain"], $data)){ $data[ $row["rain"] ] += 1 ;}
  else { $data[ $row["rain"] ] = 1 ;}
  $rdata[] = floatval($row["rain"]);
}

$stddev = standard_deviation($rdata);

$xdata = Array();
$ydata = Array();
$running = $rowcount;
$h5 = -99;
$hm = -99;
$h95 = -99;
$i=0;
for ($r=$lowVal; $r <= $hiVal; $r=$r+0.01)
{
  $xdata[] = sprintf("%.2f", $r);
  $s = sprintf("%.2f",$r);
  if (array_key_exists( $s, $data)) $running -= $data[$s];
  $c = ($running / $rowcount) * 100.0;
  $ydata[] = $c;
  if ($c <= 5 && $h5 == -99) $h5 = $i;
  if ($c <= 50 && $hm == -99) $hm = $i;
  if ($c <= 95 && $h95 == -99) $h95 = $i;
  $i+=1;
}
pg_close($coop);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;


$graph = new Graph(600,400,"example1");
$graph->SetScale("textlin",0,100);
$graph->img->SetMargin(40,5,35,60);

$graph->xaxis->SetTickLabels($xdata);
$graph->xaxis->SetTextTickInterval(100);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTitle("Precip [inches]");
$graph->xaxis->SetTitleMargin(30);

$graph->yaxis->SetTitle("Cumulative Distribution (percent)");

$graph->title->Set($cities[strtoupper($station)]['name'] ." Precip Accumulation Probabilities");
$graph->subtitle->Set($subtitle);

$l1=new LinePlot($ydata);
$l1->SetColor("blue");
$l1->SetWeight(2);
$l1->AddArea($hm,$hm,LP_AREA_FILLED,"lightred");
$l1->AddArea($h95,$h95,LP_AREA_FILLED,"lightred");
$l1->AddArea($h5,$h5,LP_AREA_FILLED,"lightred");

$txt = new Text("Diagnostics
  Min: $lowVal ($lowYear)
  95%: ". ($lowVal + ($h95 * 0.01)) ."
~Mean: ". ($lowVal + ($hm * 0.01)) ."
   SD: $stddev
   5%: ". ($lowVal + ($h5 * 0.01)) ."
  Max: $hiVal ($hiYear)
");
$txt->SetPos(0.71,0.128);
$txt->SetFont(FF_FONT1, FS_NORMAL);
$txt->SetColor("blue");


$graph->Add($l1);
$graph->Add($txt);
$graph->Stroke();

?>
