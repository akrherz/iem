<h3 class="heading"><?php echo $sname; ?></h3>
<form method="GET">
&nbsp; &nbsp; <b>Switch to:</b>
<?php
 /* Network Selector Widget */
 include_once("/mesonet/php/lib/selectWidget.php");
 $sw2 = new selectWidget("/sites/site.php", "/sites/site.php?", $network);
 echo $sw2->siteSelectInterface($station); 
?> <a href="locate.php?network=<?php echo $network; ?>">select from map</a>
</form>

<?php
  echo '<div id="iem-section">';
  echo '<center><table><tr>';
  $sites='<th><a href="/sites/site.php?station='.$station.'">Site Info</a></th>';
  $conditions='<th><a href="/sites/current.php?station='.$station.'">Current Conditions</a></th>';
  $parms='<th><a href="/sites/parm.php?station='.$station.'">Parameters</a></th>';
  $pics='<th><a href="/sites/pics.php?station='.$station.'&dir=N">Photos</a></th>';
//  $facts='<th><a href="/sites/facts.php?id='.$id.'">Facts</a></th>';
  $neighbors='<th><a href="/sites/neighbors.php?station='.$station.'">Neighbors</a></th>';
  $mapping='<th><a href="/sites/mapping.php?station='.$station.'">Location Maps</a></th>';
  $cal='<th><a href="/sites/cal.phtml?station='.$station.'">Calibrations</a></th>';


  switch($current){
   case "sites":
    $sites='<th>Site Info</th>';
    break;
   case "conditions":
    $conditions='<th>Current Conditions</th>';
    break;
   case "parms":
    $parms='<th>Parameters</th>';
    break;
   case "pics":
    $pics='<th>Photos</th>';
    break;
   case "maps":
    $mapping='<th>Location Maps</th>';
    break;
   case "cal":
    $cal='<th>Calibrations</th>';
    break;
   case "neighbors":
    $neighbors='<th>Neighbors</th>';
    break;
}

    echo $sites;
    echo $conditions;
    echo $parms;
    echo $pics;
    echo $cal;
    echo $mapping;
//    echo $facts;
    echo $neighbors;
  echo '<th>&nbsp;</th>';
  echo '</tr></table></center></div>';
?>
