<?php
/**
 * Library for doing repetetive forms stuff
 */

function minuteSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<60;$i++) {
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". $i ."</option>";
  }
  echo "</select>\n";
}

function local5MinuteSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<60;$i=$i+5) {
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo sprintf(">%02d</option>", $i );
  }
  echo "</select>\n";
}

function hourSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    $ts = mktime($i,0,0,1,1,0);
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". strftime("%I %p" ,$ts) ."</option>";
  }
  echo "</select>\n";
}

function gmtHourSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". $i ." Z</option>";
  }
  echo "</select>\n";
}


function monthSelect($selected, $name="month", $fmt="%B"){
  $s = "<select name='$name'>\n";
  for ($i=1; $i<=12;$i++) {
    $ts = mktime(0,0,0,$i,1,0);
    $s .= "<option value='".$i ."' ";
    if ($i == intval($selected)) $s .= "SELECTED";
    $s .= ">". strftime($fmt ,$ts) ."</option>";
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
    $s .= ">". $i ."</option>";
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
    echo ">". $i ."</option>";
  }
  echo "</select>\n";
}



function monthSelect2($selected, $name){
  echo "<select name='$name'>\n";
  for ($i=1; $i<=12;$i++) {
    $ts = mktime(0,0,0,$i,1,0);
    echo "<option value='".$i ."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". strftime("%B" ,$ts) ."</option>";
  }
  echo "</select>\n";
}


function daySelect($selected){
  echo "<select name='day'>\n";
  for ($k=1;$k<32;$k++){
    echo "<option value=\"".$k."\" ";
    if ($k == (int)$selected){
      echo "SELECTED";
    }
    echo ">".$k."</option>";
  }
  echo "</select>\n";
} // End of daySelect
function daySelect2($selected, $name){
  echo "<select name='$name'>\n";
  for ($k=1;$k<32;$k++){
    echo "<option value=\"".$k."\" ";
    if ($k == (int)$selected){
      echo "SELECTED";
    }
    echo ">".$k."</option>";
  }
  echo "</select>\n";
} // End 

?>
