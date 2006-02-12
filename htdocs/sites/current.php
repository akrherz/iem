<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

        $current="conditions";
	$TITLE = "IEM | Current Data";
	include("$rootpath/include/header.php"); 
        include("$rootpath/include/nav_site.php");
        include("$rootpath/include/getcurrent.php");
        include("$rootpath/include/mlib.php");


?><br>
         <div class="text"> <TABLE>
            <?php printTable($station,$network); ?> 
          </TABLE>
        </TD>
</TR>
</TABLE></div>
<?php include("$rootpath/include/footer.php"); ?>
