<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
/* We need to get some CGI vars! */
$year = isset($_GET['year']) ? $_GET['year'] : date("Y");
$month = isset($_GET['month']) ? $_GET['month'] : date("m");
$day = isset($_GET['day']) ? $_GET['day'] : date("d");
$var = isset($_GET['var']) ? $_GET['var'] : "netrad";

$titles = Array("rn_total_avg" => "Net Radiation",
  "shf1_avg" => "Soil Heat Flux",
  "le_wpl" => "Latent Heat Flux",
  "fc_wpl" => "Carbon Dioxide",
  "hs" => "Sensible Heat Flux");

$units = Array("rn_total_avg" => "Wm^-2",
  "shf1_avg" => "Wm^-2",
  "le_wpl" => "Wm^-2",
  "fc_wpl" => "mg/m^2/s",
  "hs" => "Wm^-2");

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

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

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

// Create the linear plot
$a = $rad['nstl11'];
$lineplot=new LinePlot($a);
$lineplot->SetColor("red");
$lineplot->SetLegend("NSTL11");
$lineplot->SetWeight(2);
$graph->Add($lineplot);

$b = $rad['nstl10'];
$lineplot2=new LinePlot($b);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("NSTL10");
$lineplot2->SetWeight(2);
$graph->Add($lineplot2);

// Create the linear plot
$b = $rad['nstlnsp'];
$lineplot3=new LinePlot($b);
$lineplot3->SetColor("black");
$lineplot3->SetLegend("NSPR");
$lineplot3->SetWeight(2);
$graph->Add($lineplot3);

// Create the linear plot
$b = $rad['nstl30ft'];
$lineplot4=new LinePlot($b);
$lineplot4->SetColor("green");
$lineplot4->SetLegend("NSTL30FT");
$lineplot4->SetWeight(2);
$graph->Add($lineplot4);


// Display the graph
$graph->Stroke();
?>

