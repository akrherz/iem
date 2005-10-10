<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
/* We need to get some CGI vars! */
$year = isset($_GET['year']) ? $_GET['year'] : date("Y");
$month = isset($_GET['month']) ? $_GET['month'] : date("m");
$day = isset($_GET['day']) ? $_GET['day'] : date("d");
$var = isset($_GET['var']) ? $_GET['var'] : "netrad";

$titles = Array("netrad" => "Net Radiation",
  "soilheat" => "Soil Heat Flux",
  "latent" => "Latent Heat Flux",
  "co2" => "Carbon Dioxide",
  "sensible" => "Sensible Heat Flux");

$units = Array("netrad" => "Wm^-2",
  "soilheat" => "Wm^-2",
  "latent" => "Wm^-2",
  "co2" => "mg/m^2/s",
  "sensible" => "Wm^-2");

$pgconn = iemdb("other");

$sql = sprintf("SELECT * from flux%s WHERE date(valid) = '%s-%s-%s' ORDER by valid ASC", $year, $year, $month, $day);

$rs = pg_exec($pgconn, $sql);
$sts = mktime(0,0,0,$month, $day, $year);

$rad = array("corn" => array(), "sbean" => array(), "nspr" => array() );
$xlable = array();
for ($i=0;$i<48;$i++)
{
  $rad['nstl11'][$i] = "";
  $rad['nstl10'][$i] = "";
  $rad['nspr'][$i] = "";
  $xlabel[$i] = date("h:i A", $sts + ($i * 1800));
}

$havedata = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{ 
  $ts = strtotime( substr($row["valid"],0,16) );
  $offset = ($ts - $sts) / (30*60); // 30 min
  $stid = $row["station"];
  $havedata[$stid] = 1;
  if (floatval($row[$var]) > -99){
  $rad[$stid][$offset]  = $row[$var];
  }
}

$rs = pg_exec($pgconn, sprintf("SELECT * from flux_meta WHERE sts < '%s-%s-%s' and ets > '%s-%s-%s'", $year, $month, $day, $year, $month, $day) );
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $st = $row["station"];
  if ($st == 'nstl11') $nstl11_lbl = "Over ". $row["surface"];
  if ($st == 'nstl10') $nstl10_lbl = "Over ". $row["surface"];
}

$ts_lbl = date("d F Y", $ts);

pg_close($pgconn);

include ("/mesonet/php/include/jpgraph/jpgraph.php");
include ("/mesonet/php/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,350);
$graph->SetScale("textlin");
$graph->img->SetMargin(50,40,45,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set($titles[$var] ." Timeseries for ${ts_lbl}");

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->yaxis->SetTitle($titles[$var] ." [". $units[$var] ."]");
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(37);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");

if ($havedata['nstl11']) {
// Create the linear plot
$a = $rad['nstl11'];
$lineplot=new LinePlot($a);
$lineplot->SetColor("red");
$lineplot->SetLegend($nstl11_lbl);
$lineplot->SetWeight(2);
$graph->Add($lineplot);
}

if ($havedata['nstl10']) {
// Create the linear plot
$b = $rad['nstl10'];
$lineplot2=new LinePlot($b);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend($nstl10_lbl);
$lineplot2->SetWeight(2);
$graph->Add($lineplot2);
}

if ($havedata['nspr']) {
// Create the linear plot
$b = $rad['nspr'];
$lineplot3=new LinePlot($b);
$lineplot3->SetColor("black");
$lineplot3->SetLegend("Over Prairie");
$lineplot3->SetWeight(2);
$graph->Add($lineplot3);
}

// Display the graph
$graph->Stroke();
?>

