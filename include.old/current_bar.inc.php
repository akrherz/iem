<table width="100%" border=1 cellspacing=0 cellpadding=1>
<tr>
 <th colspan="7" bgcolor="#CCCCCC">Select Network</th></tr>
<tr>
<?php
  $d = Array(
    "ASOS" => Array("url" => "/ASOS/current.phtml"),
    "AWOS" => Array("url" => "/AWOS/current.phtml"),
    "COOP" => Array("url" => "/COOP/current.phtml"),
    "DCP" => Array("url" => "/DCP/current.phtml"),
    "SchoolNet" => Array("url" => "/schoolnet/current.phtml"),
    "OT" => Array("url" => "/other/current.phtml"),
    "RWIS" => Array("url" => "/RWIS/current.phtml"),
    "RWIS_SF" => Array("url" => "/RWIS/currentSF.phtml"),
    "SCAN" => Array("url" => "/scan/current.phtml"),
    "My Favorites" => Array("url" => "/my/current.phtml"),
    "Road Conditions" => Array("url" => "/current/rc.phtml"),
    "All" => Array("url" => "/current/all.phtml") );
  
  $i = 0;
  while ( list($key, $value) = each($d) ){
    echo "<th ";
    if ($current_network == $key) 
       echo "bgcolor=\"#666666\"><font color=\"white\">$key</font></th>";
    else 
       echo "><a href=\"". $value["url"] ."\">$key</a></th>";
    if ($i == 5) echo "</tr><tr>";
    $i++;
  }
?>

</tr></table>
