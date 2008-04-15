

<form method="GET" action="camera.phtml">
<input type="hidden" value="<?php echo $network; ?>" name="network"> 
<table><caption>Time Settings:</caption>
<thead><tr><th>&nbsp;</th><th>Year:</th><th>Month:</th><th>Day:</th><th>Hour:</th><th>Minute</th><td></td></tr></thead>
<tbody>
<tr>
<td><input type="checkbox" value="yes" name="archive" <?php if($isarchive) echo "CHECKED=CHECKED"; ?>>Archived Images</td>
<td><?php echo yearSelect(2008, $year, "year"); ?></td>
<td><?php echo monthSelect($month, "month"); ?></td>
<td><?php echo daySelect($day, "day"); ?></td>
<td><?php echo hourSelect($hour, "hour"); ?></td>
<td><?php echo minuteSelect($minute, "minute"); ?></td>
<td><input type="submit" value="GO!"></td>
</tr>
</tbody></table>
</form>

<?php $t = time(); ?>

<?php
 include("camrad.php");
 $misstxt = "Cameras Missing: ";
 reset($cameras);
 while (list($id, $v) = each($cameras))
 {
   if ($v["network"] != $network){ continue; }
   if (! $v["active"] ){
     if ($id == "S03I4" || $id == "SMAI4" || $id == "SCAI4") continue;
     $misstxt .= $v["name"] ." , ";
     continue;
   }
   echo sprintf("<div style=\"float: left; margin-left: 5px;\"><b>%s. %s, %s</b> (%s County)<br /><img src=\"%s\"></div>", $v["num"], $v["name"], $v["state"], $v["county"], $v["url"]);
 }
?>



<br style="clear: both;">

<p><b>Cool Shots!</b>
