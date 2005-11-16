<h3 class="heading"><?php echo $sname; ?></h3>
<form method="GET">
&nbsp; &nbsp; <b>Switch to:</b>
<?php
 /* Network Selector Widget */
 include_once("$rootpath/include/selectWidget.php");
 $sw2 = new selectWidget("$rooturl/sites/site.php", "$rooturl/sites/site.php?", $network);
 echo $sw2->siteSelectInterface($station); 
?> <a href="locate.php?network=<?php echo $network; ?>">select from map</a>
</form>

<?php
  echo '<div id="iem-section">';
  echo '<center><table><tr>';
  $sites='<th><a href="'.$rooturl.'/sites/site.php?network='.$network.'&station='.$station.'">Site Info</a></th>';
  $conditions='<th><a href="'.$rooturl.'/sites/current.php?network='.$network.'&station='.$station.'">Current Conditions</a></th>';
  $parms='<th><a href="'.$rooturl.'/sites/parm.php?network='.$network.'&station='.$station.'">Parameters</a></th>';
  $pics='<th><a href="'.$rooturl.'/sites/pics.php?network='.$network.'&station='.$station.'&dir=N">Photos</a></th>';
//  $facts='<th><a href="/sites/facts.php?id='.$id.'">Facts</a></th>';
  $neighbors='<th><a href="'.$rooturl.'/sites/neighbors.php?network='.$network.'&station='.$station.'">Neighbors</a></th>';
  $mapping='<th><a href="'.$rooturl.'/sites/mapping.php?network='.$network.'&station='.$station.'">Location Maps</a></th>';
  $cal='<th><a href="'.$rooturl.'/sites/cal.phtml?network='.$network.'&station='.$station.'">Calibrations</a></th>';


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
