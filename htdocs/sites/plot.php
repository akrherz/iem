<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

 $TITLE = "IEM | Sites";
 include("$rootpath/include/header.php");

 $prod = isset($_GET["prod"]) ? $_GET["prod"]: 0;
 $current = "7dayhilo"; 
 if ($prod == 1) $current = "monthhilo";
 include("sidebar.php"); 
 $products = Array(
0 => "7day_hilo_plot.php",
1 => "month_hilo_plot.php",
);
?>
<div style="float: left;">
 <img src="<?php echo sprintf("%s?network=%s&station=%s", $products[$prod], $network, $station); ?>">
</div>
<?php include("$rootpath/include/footer.php"); ?>
