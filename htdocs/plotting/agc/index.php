<?php 
include("../../../config/settings.inc.php");
include_once "../../../include/myview.php";
$t = new MyView();
$t->title = "ISU Ag Plotting";
$t->thispage="networks-agclimate";

require_once "../../../include/forms.php"; 
include("../../../include/imagemaps.php"); 
$plot = isset($_GET["plot"]) ? xssafe($_GET["plot"]): "solarRad";
$station = isset($_GET["station"]) ? xssafe($_GET["station"]): "A130209";

$desc = Array(
  "solarRad" => "This plot shows hourly observations of solar radiation (red),
   4 inch soil temperature (green), and 2 meter air temperature (blue). This
   plot often illustrates the difference between the soil's thermal inertia 
   and the air with the soil temperature lagging the air temperature by a 
   few hours.",
  "l30temps" => "A simple plot of daily observed high and low 2 meter air
   temperatures during the past 30 days",
  "l60rad" => "There is a lot going on in this plot!  The bars are daily 
   observations of solar radiation.  The red dashed line is a solar radiation
   climatology based on observations from this site.  The blue line are 
   daily average 4 inch soil temperature observations with the purple dashed
   line being the climatology for the site.",
  "l60p-et" => "An accumulated difference plot of observed precipitation minus 
   estimated potential evapotranspiration.  This plot gives a first guess at
   near term water supply for vegetation.  The precipitation data going into
   this plot is not valid during the cold season and underestimated during the
   rainy season.  So use this plot with care."
  );

$imgurl = sprintf("%s.php?station=%s", $plot, $station);
$nselect = isuagSelect( $station);

$ar = Array(
		"solarRad" => "Yesterday Solar Radiation &amp; Air Temps",
  "l30temps" => "High/low temps for last 30 days",
  "l60rad" => "4 inch soil temps and radiation for last 60 days",
  "l60p-et" => "60 days of Precip minus PET");
$pselect = make_select("plot", $plot, $ar);

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">ISU Ag Climate</a></li>
 </ol>

<form name="selector" method="GET">
<p><strong>Select Plot:</strong>
{$pselect}

<strong>Select Site:</strong>
{$nselect}

<input type="submit" value="Make Plot"></form>

<p><img src="{$imgurl}">

<p><strong>Plot Description:</strong>
<br />{$desc[$plot]}
EOF;
$t->render('single.phtml');
?>
