<?php 
include("setup.php");

        $current="conditions";
	$TITLE = "IEM | Current Data";
	include("/mesonet/php/include/header.php"); 
        include("../include/nav_site.php");
        include("../include/getcurrent.php");
        include("../include/mlib.php");


?><br>
         <div class="text"> <TABLE>
            <?php printTable($station,$network); ?> 
          </TABLE>
        </TD>
</TR>
</TABLE></div>
<?php include("/mesonet/php/include/footer.php"); ?>
