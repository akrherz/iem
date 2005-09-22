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
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    $ts = mktime($i,0,0,1,1,0);
    echo "<option value='".$i."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". strftime("%I %p" ,$ts) ."\n";
  }
  echo "</select>\n";
}

function gmtHourSelect($selected, $name){
  echo "<select name='".$name."'>\n";
  for ($i=0; $i<24;$i++) {
    echo "<option value='".$i."'>". $i ." Z\n";
  }
  echo "</select>\n";
}


function monthSelect($selected){
  echo "<select name='month'>\n";
  for ($i=1; $i<=12;$i++) {
    $ts = mktime(0,0,0,$i,1,0);
    echo "<option value='".$i ."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". strftime("%B" ,$ts) ."\n";
  }
  echo "</select>\n";
}

function yearSelect($start, $selected){
  $start = intval($start);
  $now = time();
  $tyear = strftime("%Y", $now);
  echo "<select name='year'>\n";
  for ($i=$start; $i<=$tyear;$i++) {
    echo "<option value='".$i ."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". $i ."\n";
  }
  echo "</select>\n";
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



function monthSelect2($selected, $name){
  echo "<select name='$name'>\n";
  for ($i=1; $i<=12;$i++) {
    $ts = mktime(0,0,0,$i,1,0);
    echo "<option value='".$i ."' ";
    if ($i == intval($selected)) echo "SELECTED";
    echo ">". strftime("%B" ,$ts) ."\n";
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
    echo ">".$k."\n";
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
    echo ">".$k."\n";
  }
  echo "</select>\n";
} // End 

?>
