<?php
/**
 * Library for doing repetetive forms stuff
 */

function localMinuteSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<60;$i++) {
    echo "<option value='".$i."'>". $i ."\n";
  }
  echo "</select>\n";
}

function local5MinuteSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<60;$i=$i+5) {
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". $i ."\n";
  }
  echo "</select>\n";
}

function localHourSelect($selected, $name){
  $s = "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    $ts = mktime($i,0,0,1,1,0);
    $s .= "<option value='".$i."' ";
    if ($i == intval($selected)) $s .= "SELECTED";
    $s .= ">". strftime("%I %p" ,$ts) ."\n";
  }
  $s .= "</select>\n";
  return $s;
}

function gmtHourSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    echo "<option value='".$i."'>". $i ." Z\n";
  }
  echo "</select>\n";
}


function monthSelect($selected, $sname){
  $s = "<select name='$sname'>\n";
  for ($i=1; $i<=12;$i++) {
    $ts = mktime(0,0,0,$i,1,0);
    $s .= "<option value='".$i ."' ";
    if ($i == intval($selected)) $s .= "SELECTED";
    $s .= ">". strftime("%B" ,$ts) ."\n";
  }
  $s .= "</select>\n";
	return $s;
}

function yearSelect($start, $selected){
	$start = intval($start);
	$now = time();
	$tyear = strftime("%Y", $now);
	$s = "<select name='year'>\n";
	for ($i=$start; $i<=$tyear;$i++) {
 		$s .= "<option value='".$i ."' ";
		if ($i == intval($selected)) $s .= "SELECTED";
		$s .= ">". $i ."\n";
	}
	$s .= "</select>\n";
	return $s;
}

function yearSelect2($start, $selected, $fname){
  $start = intval($start);
  $now = time();
  $tyear = strftime("%Y", $now);
  echo "<select name='$fname'>\n";
  for ($i=$start; $i<=$tyear;$i++) {
    echo "<option value='".$i ."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". $i ."\n";
  }
  echo "</select>\n";
}



function dayOffsetSelect($selected, $name="day")
{
  $s = "<select name='$name'>\n";
  for ($k=0;$k<3;$k++)
  {
    $s .= "<option value=\"".$k."\" ";
    if ($k == (int)$selected){
      $s .= "SELECTED";
    }
    $s .= ">Day".$k."\n";
  }
  $s .= "</select>\n";
  return $s;
}

function daySelect($selected, $name="day"){
	$s = "<select name='$name'>\n";
	for ($k=1;$k<32;$k++){
		$s .= "<option value=\"".$k."\" ";
		if ($k == (int)$selected){
			$s .= "SELECTED";
		}
		$s .= ">".$k."\n";
	}
	$s .= "</select>\n";
	return $s;
} // End of daySelect


?>
