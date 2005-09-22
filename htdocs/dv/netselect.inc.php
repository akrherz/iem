<?php 
 /** Handle Selection of network */

$ns_networks = Array(
  "IA_ASOS" => "ASOS [Iowa]",
  "AWOS"    => "AWOS [Iowa]",
  "KCCI"    => "KCCI SchoolNet [Iowa]",
  "KELO"    => "KELO WeatherNet [IA,SD,MN]");
?>

<div style="background: #eeeeee">

<form method="GET" name="switchNetwork">

<b>Select Network:</b><select name="id"
 onChange="location=this.form.id.options[this.form.id.selectedIndex].value">
<?php
while( list($key, $val) = each($ns_networks) ){
 echo "<option value=\"$urlbase/$ttype/$valid/$mode/$key/$sortcol/$sortdir\" ";
 if ($id == $key) echo "selected=\"selected\"";
 echo ">". $ns_networks[$key] ."\n";
}
?></select>
</form>
</div>
