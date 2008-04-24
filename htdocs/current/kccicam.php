
<form method="GET" action="camera.phtml">
<input type="hidden" value="<?php echo $network; ?>" name="network"> 
<table><caption>Time Settings:</caption>
<thead><tr><th>&nbsp;</th><th>Year:</th><th>Month:</th><th>Day:</th><th>Hour:</th><th>Minute</th><td></td></tr></thead>
<tbody>
<tr>
<td><input type="checkbox" value="yes" name="archive" <?php if($isarchive) echo "CHECKED=CHECKED"; ?>>Archived Images</td>
<td><?php echo yearSelect(2003, $year, "year"); ?></td>
<td><?php echo monthSelect($month, "month"); ?></td>
<td><?php echo daySelect($day, "day"); ?></td>
<td><?php echo hourSelect($hour, "hour"); ?></td>
<td><?php echo minuteSelect($minute, "minute"); ?></td>
<td><input type="submit" value="GO!"></td>
</tr>
</tbody></table>
</form>

<?php $t = time(); ?>

<div style="float: left; margin-left: 5px;"><b>Radar View</b><br />
<img src="camrad.php?network=<?php echo $network; ?>&ts=<?php echo date("YmdHi", $radts);?>"></div>


<?php
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
<ul>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2004&month=6&day=11&hour=19&minute=32">11 Jun 2004 - 7:32 PM, Webster City Tornado</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2005&month=5&day=26&hour=19&minute=15">26 May 2005 - 7:15 PM, Pella Double Rainbow</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2005&month=6&day=8&hour=20&minute=55">8 Jun 2005 - 8:55 PM, All sorts of colours</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2005&month=9&day=8&hour=12&minute=30">8 Sep 2005 - 12:30 PM, Blurry shot of Ames Tornado</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2005&month=11&day=12&hour=16&minute=38">12 Nov 2005 - 4:38 PM, Woodward tornado from Madrid</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2005&month=11&day=12&hour=17&minute=00">12 Nov 2005 - 5:00 PM, Ames tornado</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2006&month=07&day=17&hour=16&minute=50">17 Jul 2006 - 4:50 PM, Tama possible brief tornado</a></li>
 <li><a href="http://mesonet.agron.iastate.edu/current/camera.phtml?archive=yes&year=2007&month=10&day=2&hour=17&minute=56">2 Oct 2007 - 5:56 PM, Twin Cedars possible tornado</a></li>
</ul>
