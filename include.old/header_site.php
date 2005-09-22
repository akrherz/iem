<?php

  echo '<TABLE class="page" style="padding: 0;" bgcolor="#DDDDDD">
         <tr>';
  $sites='<td class="hlink"><a class="hlink" href="/sites/site.php?id='.$id.'">Info</a></td>';
  $conditions='<td class="hlink"><a class="hlink" href="/sites/current.php?id='.$id.'">
             Current Conditions</a></td>';
  $parms='<td class="hlink"><a class="hlink" href="/sites/parm.php?id='.$id.'">Parameters</a></td>';
  $pics='<td class="hlink"><a class="hlink" href="/sites/pics.php?id='.$id.'&dir=N">Photos</a></td>';
//  $facts='<td class="hlink"><a class="hlink" href="/sites/facts.php?id='.$id.'">Facts</a></td>';
  $neighbors='<td class="hlink"><a class="hlink" href="/sites/neighbors.php?id='.$id.'">Neighbors</a></td>';

  switch($current){
   case "sites":
    $sites='<td class="hlink"><a class="alink">Info</a></td>';
    break;
   case "conditions":
    $conditions='<td class="hlink"><a class="alink">Current Conditions</a></td>';
    break;
   case "parms":
    $parms='<td class="hlink"><a class="alink">Parameters</a></td>';
    break;
   case "pics":
    $pics='<td class="hlink"><a class="alink">Photos</a></td>';
    break;
//   case "facts":
//    $facts='<td class="hlink"><a class="alink">Facts</a></td>';
//    break;
   case "neighbors":
    $neighbors='<td class="hlink"><a class="alink">Neighbors</a></td>';
    break;
}  

    echo $sites;
    echo '<th>|</th>';
    echo $conditions;
    echo '<th>|</th>';
    echo $parms;
    echo '<th>|</th>';
    echo $pics;
    echo '<th>|</th>';
//    echo $facts;
//    echo '<th>|</th>';
//
    echo $neighbors;
    echo '</tr>';
    echo '<tr bgcolor="black"><td colspan="13"><img src="/icons/spacer.gif" height="0" border="0" width="0" ALT="Spacer">
          </td></tr>';
    echo '</TABLE>';
    echo '&nbsp;&nbsp;';

?>
