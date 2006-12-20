<?php
putenv("TZ=GMT"); /* Hack around timezone problem */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
/* We need to get some CGI vars! */
$year = isset($_GET['year']) ? $_GET['year'] : die();
$month = isset($_GET['month']) ? $_GET['month'] : die();
$day = isset($_GET['day']) ? $_GET['day'] : die();
$pvar = isset($_GET['pvar']) ? $_GET['pvar'] : die();
$sts = mktime(0,0,0,$month, $day, $year);

$vars = Array();
$pgconn = iemdb("other");

$sql = "SELECT * from flux_vars ORDER by details ASC";
$rows = pg_exec($pgconn, $sql);
for( $i=0; $row = @pg_fetch_array($rows,$i); $i++)
{
  $vars[ $row["name"] ] = Array("units" => $row["units"], "details" => $row["details"]);
}


$sql = sprintf("SELECT * from flux%s WHERE date(valid) = '%s-%s-%s' and $pvar IS NOT NULL ORDER by valid ASC", $year, $year, $month, $day);
$rs = pg_exec($pgconn, $sql);

$data = Array("nstl11" => Array(),
   "nstl10" => Array(),
   "nstl30ft" => Array(),
   "nstlnsp" => Array() );
$times = Array("nstl11" => Array(),
   "nstl10" => Array(),
   "nstl30ft" => Array(),
   "nstlnsp" => Array() );

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{ 
  $ts = strtotime( substr($row["valid"],0,16) );
  $stid = $row["station"];
  $data[$stid][] = floatval($row[$pvar]);
  $times[$stid][] = $ts;
}

$rs = pg_exec($pgconn, sprintf("SELECT * from flux_meta WHERE sts < '%s-%s-%s' and ets > '%s-%s-%s'", $year, $month, $day, $year, $month, $day) );
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $st = $row["station"];
  if ($st == 'nstl11') $nstl11_lbl = "Over ". $row["surface"];
  if ($st == 'nstl10') $nstl10_lbl = "Over ". $row["surface"];
}

$ts_lbl = date("d F Y", $sts);

pg_close($pgconn);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,350);
$graph->SetScale("datlin");
$graph->img->SetMargin(50,40,45,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set($vars[$pvar]["details"]);
$graph->subtitle->Set(" Timeseries for ${ts_lbl}");

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->yaxis->SetTitle($vars[$pvar]["details"] ." [". $vars[$pvar]["units"] ."]");
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(37);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.9, "left", "top");

// Create the linear plot
if (sizeof($data["nstl11"]) > 1) {
 $lineplot=new LinePlot($data["nstl11"], $times["nstl11"]);
 $lineplot->SetColor("red");
 $lineplot->SetLegend("NSTL11");
 $lineplot->SetWeight(2);
 $graph->Add($lineplot);
}

if (sizeof($data["nstl10"]) > 1) {
 $lineplot2=new LinePlot($data["nstl10"], $times["nstl10"]);
 $lineplot2->SetColor("blue");
 $lineplot2->SetLegend("NSTL10");
 $lineplot2->SetWeight(2);
 $graph->Add($lineplot2);
}

// Create the linear plot
if (sizeof($data["nstlnsp"]) > 1) {
 $lineplot3=new LinePlot($data["nstlnsp"], $times["nstlnsp"]);
 $lineplot3->SetColor("black");
 $lineplot3->SetLegend("NSPR");
 $lineplot3->SetWeight(2);
 $graph->Add($lineplot3);
}

// Create the linear plot
if (sizeof($data["nstl30ft"]) > 1) {
 $lineplot4=new LinePlot($data["nstl30ft"], $times["nstl30ft"]);
 $lineplot4->SetColor("green");
 $lineplot4->SetLegend("NSTL30FT");
 $lineplot4->SetWeight(2);
 $graph->Add($lineplot4);
}

// Display the graph
$graph->Stroke();
?>

