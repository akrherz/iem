<?php
include("../../include/vtec.php");

//while( list($key, $value) = each($vtec_significance) ){
while( list($key, $value) = each($vtec_phenomena) ){
  echo "['$key','$value'],\n";
} 

?>
