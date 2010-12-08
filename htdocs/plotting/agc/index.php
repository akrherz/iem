<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | ISU Ag Plotting";
$THISPAGE="networks-agclimate";
include("$rootpath/include/header.php"); 
include("$rootpath/include/forms.php"); 
include("$rootpath/include/imagemaps.php"); 
$plot = isset($_GET["plot"]) ? $_GET["plot"] : "solarRad";
$station = isset($_GET["station"]) ? $_GET["station"] : "A130209";

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

?>

Back to <a href="/agclimate/">ISU Ag Climate</a> Homepage.<p>

<form name="selector" method="GET">
<p><strong>Select Plot:</strong>
<select name="plot">
  <option value="solarRad" <?php if ($plot == "solarRad") echo "SELECTED"; ?>>Yesterday Solar Radiation & Air Temps</option>
  <option value="l30temps" <?php if ($plot == "l30temps") echo "SELECTED"; ?>>High/low temps for last 30 days</option>
  <option value="l60rad" <?php if ($plot == "l60rad") echo "SELECTED"; ?>>4 inch soil temps and radiation for last 60 days</option>
  <option value="l60p-et" <?php if ($plot == "l60p-et") echo "SELECTED"; ?>>60 days of Precip minus PET</option>
</select>

<strong>Select Site:</strong>
<?php echo isuagSelect( $station); ?>

<input type="submit" value="Make Plot"></form>

<p><img src="<?php echo sprintf("%s.php?station=%s", $plot, $station); ?>">

<p><strong>Plot Description:</strong>
<br /><?php echo $desc[$plot]; ?>

<?php include("$rootpath/include/footer.php"); ?>
