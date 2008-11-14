<?php
include("../../../config/settings.inc.php");

$station = isset($_GET['station']) ? $_GET['station'] : "DSM";
$year = isset($_GET['year']) ? $_GET['year']: date("Y");
$feature = isset($_GET["feature"]);


include("$rootpath/include/iemaccess.php");
include("$rootpath/include/station.php");
$st = new StationData($station);
$st->load_station( $st->table[$station]["climate_site"]);
$cities = $st->table;

$coopdb = iemdb("coop");
$iem = new IEMAccess();

$climate_site = $cities[$station]["climate_site"];

$q = "SELECT sum(pday) as rain, extract(month from day) as month from summary_$year
		WHERE station = '$station' and pday >= 0 GROUP by month ORDER by month ASC";
$rs = $iem->query($q);
$obs = Array();
$aobs = Array();
$atot = 0;
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
	$p = $row["rain"];
	if ($p < 0) $p = 0;
	$atot += $p;
	$aobs[$i] = $atot;
	$obs[$i] = $p;
}

/* Now we need the climate data */
$q = "SELECT sum(precip) as rain, extract(month from valid) as month from climate
		WHERE station = '". strtolower($climate_site) ."' and (extract(doy from valid) < extract(doy from now()) or $year != extract(year from now()) ) GROUP by month
		ORDER by month ASC";
$rs = pg_exec($coopdb, $q);
$climate = Array();
$cdiff = Array();
$aclimate = Array();
$atot = 0;
$zeros = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{
	$p = $row["rain"];
	$climate[$i] = $p;
	$atot += $p;
	$cdiff[$i] = $aobs[$i] - $atot ;
	$aclimate[$i] = $atot;
	$zeros[$i] = 0;
}

pg_close($coopdb);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

$width = 640;
$height = 480;
if ($feature){
  $width = 300;
  $height = 250;
}

$graph = new Graph($width,$height);
$graph->SetScale("textlin");
$graph->img->SetMargin(45,10,40,30);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->SetTitleMargin(32);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitle("Month of Year");

$graph->yaxis->SetTitle("Precipitation (in)");
$graph->title->Set( $cities[$station]["name"] ." [$station] $year Precip");
$graph->subtitle->Set("Climate Site: ". $cities[strtoupper($climate_site)]["name"] ."[". $climate_site ."]");
$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->Pos(0.15, 0.15, "left", "top");

// Create the linear plot
$b1plot =new BarPlot($climate);
$b1plot->SetFillColor("red");
$b1plot->SetLegend("Climate");
$b2plot = new BarPlot($obs);
$b2plot->SetFillColor("blue");
$b2plot->SetLegend("Obs Rain");
$g = new GroupBarPlot(array($b1plot,$b2plot));
$g->SetAlign("center");

// Create the linear plot
$lp1=new LinePlot($aobs);
$lp1->SetLegend("Actual Accum");
$lp1->SetColor("blue");
$lp1->SetWeight(2);
$lp1->value->SetFormat('%.2f');
$lp1->value->Show();
$lp1->value->SetMargin(14);

$lp2=new LinePlot($aclimate);
$lp2->SetLegend("Climate Accum");
$lp2->SetColor("red");
$lp2->SetWeight(2);

$z = new LinePlot($zeros);
$z->SetWeight(2);

// Add the plot to the graph
$graph->Add($lp1);
$graph->Add($lp2);
$graph->Add($g);
$graph->Add($z);

// Display the graph
$graph->Stroke();
?>
