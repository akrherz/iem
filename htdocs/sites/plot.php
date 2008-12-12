<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/forms.php");
include("setup.php");
$THISPAGE="iem-sites";
 $TITLE = "IEM | Sites";
 include("$rootpath/include/header.php");

 $prod = isset($_GET["prod"]) ? $_GET["prod"]: 0;
 $month = isset($_GET["month"]) ? $_GET["month"]: date("m");
 $year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
 $current = "7dayhilo"; 
 if ($prod == 1) $current = "monthhilo";
 if ($prod == 2) $current = "monthrain";
 include("sidebar.php"); 
 $products = Array(
0 => "7day_hilo_plot.php",
1 => "month_hilo_plot.php",
2 => "../plotting/month/rainfall_plot.php",
);
?>
<div style="float: left;">
<?php if ($prod == 1 or $prod == 2) { 
  echo "<form method=\"GET\" name=\"modify\">
 <input type=\"hidden\" name=\"station\" value=\"$station\">
 <input type=\"hidden\" name=\"network\" value=\"$network\">
 <input type=\"hidden\" name=\"prod\" value=\"$prod\">
 <h3>Select month and year:</h3>
 ". monthSelect($month) . yearSelect(2004, $year)
 ."<input type=\"submit\" value=\"Generate Plot\">
 </form>";

}
?>
 <br /><img src="<?php echo sprintf("%s?month=%s&year=%s&network=%s&station=%s", $products[$prod], $month, $year, $network, $station); ?>">
</div>
<?php include("$rootpath/include/footer.php"); ?>
