<?php
 include("../config/settings.inc.php");
 define("IEM_APPID", 39);
 include("$rootpath/include/database.inc.php");
 $dbconn = iemdb("mesosite");
 
 $TITLE = "IEM | Application Listing";
 $THISPAGE = "iem-apps";
 include("$rootpath/include/header.php");
 ?>
 <h3>IEM Application Listing</h3>
 <p>These are applications internally indexed by the IEM.  This list is created to help index content
 on this website.
 
 <p><table cellpadding="2" cellspacing="0" border="1">
 <thead>
 <tr><th>Title</th><th>Description</th><th>Tags</th></tr>
 </thead>
 <?php 
 $tags = Array();
 $rs = pg_exec($dbconn, "SELECT appid, sumtxt(tag||',') as t from iemapps_tags GROUP by appid");
 for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 	$tags[$row["appid"]] = $row["t"];
 }
 $rs = pg_exec($dbconn, "SELECT * from iemapps i ORDER by appid ASC");
 for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 	echo sprintf("<tr><th><a href='%s%s'>%s</a></th><td>%s</td><td>%s</td></tr>\n", $rooturl,
 	$row["url"],  $row["name"], $row["description"], @$tags[$row["appid"]]);
 }
 ?>
 </table>
 
 
 <?php 
 include("$rootpath/include/footer.php");
 ?>