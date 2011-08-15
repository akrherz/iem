<?php
include("../../../config/settings.inc.php");

$station = isset($_GET['station']) ? $_GET['station'] : "DSM";
$network = isset($_GET['network']) ? $_GET['network'] : "IA_ASOS";
$month = isset($_GET['month']) ? $_GET['month']: date("m");
$year = isset($_GET['year']) ? $_GET['year']: date("Y");
$ts = mktime(0,0,0, $month, 1, $year);

$today = time();

include("$rootpath/include/iemaccess.php");
include("$rootpath/include/station.php");
$st = new StationData($station, $network);
$cnetwork = sprintf("%sCLIMATE", $st->table[$station]["state"]);
$st->load_station( $st->table[$station]['climate_site'], $cnetwork );
$cities = $st->table;

$hasclimate = 1;
if ($st->table[$station]['climate_site'] == ""){ $hasclimate = 0; }

$coopdb = iemdb("coop");
$IEM = iemdb('iem');
$rs = pg_prepare($IEM, "SELECTOR", "SELECT pday, extract(day from day) as day from summary_$year
		WHERE station = $1 and network = $2 and extract(month from day) = $3 
		ORDER by day ASC");

$climate_site = $cities[$station]["climate_site"];

$rs = pg_execute($IEM, "SELECTOR", Array($station, $network, $month));
$obs = Array();
$aobs = Array();
$atot = 0;
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
	$p = $row["pday"];
	if ($p < 0) $p = 0;
	$atot += $p;
	$aobs[$i] = $atot;
	$obs[$i] = $p;
}

if ($hasclimate){
/* Now we need the climate data */
$q = "SELECT precip, extract(day from valid) as day from ncdc_climate71
		WHERE station = '". strtolower($climate_site) ."' and extract(month from valid) = $month
		ORDER by day ASC";
$rs = pg_exec($coopdb, $q);
$climate = Array();
$cdiff = Array();
$aclimate = Array();
$atot = 0;
$zeros = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{
	$obts = mktime(0,0,0, $month, $row["day"], $year);
	if ($obts > $today) break;
	$p = $row["precip"];
	$climate[$i] = $p;
	$atot += $p;
	$cdiff[$i] = $aobs[$i] - $atot ;
	$aclimate[$i] = $atot;
	$zeros[$i] = 0;
}
}
pg_close($coopdb);
pg_close($IEM);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,400);
$graph->SetScale("textlin");
$graph->SetMarginColor('white');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->xgrid->Show();

$graph->img->SetMargin(45,10,80,30);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitle("Day of Month");

$graph->yaxis->SetTitle("Precipitation (in)");
$graph->title->Set( $cities[$station]["name"] ." [$station] Precipitation for ". date("M Y", $ts) );
if ($hasclimate){
$graph->subtitle->Set("Climate Site: ". $cities[strtoupper($climate_site)]["name"] ."[". $climate_site ."]");
}
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

if($hasclimate && sizeof($cdiff) > 0){
// Create the linear plot
$b1plot =new BarPlot($cdiff);
$b1plot->SetFillColor("red");
$b1plot->SetLegend("Accum Difference");
$b2plot = new BarPlot($obs);
$b2plot->SetFillColor("blue");
$b2plot->SetLegend("Obs Rain");
$g = new GroupBarPlot(array($b1plot,$b2plot));
$g->SetAlign("left");
}

// Create the linear plot
$lp1=new LinePlot($aobs);
$lp1->SetLegend("Actual Accum");
$lp1->SetColor("blue");
$lp1->SetWeight(2);

if ($hasclimate && sizeof($cdiff) > 0){
$lp2=new LinePlot($aclimate);
$lp2->SetLegend("Climate Accum");
$lp2->SetColor("red");
$lp2->SetWeight(2);
$z = new LinePlot($zeros);
$z->SetWeight(2);
}

// Add the plot to the graph
$graph->Add($lp1);
if ($hasclimate && sizeof($cdiff) > 0){
$graph->Add($lp2);
$graph->Add($g);
$graph->Add($z);
}

// Display the graph
$graph->Stroke();
?>
