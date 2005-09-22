<?php
 /** Fill Holes */

function fillholes($ar){
 $ra = $ar;
 $lval = " ";
 while( list($key, $val) = each($ar) ){
   if ($key > 1430) break;
   if ($ar[$key] != ""){ 
     $ra[$key] = $ar[$key];
     $ra[$key + 1] = $ar[$key];
     $ra[$key + 2] = $ar[$key];
     $ra[$key + 3] = $ar[$key];
     $ra[$key + 4] = $ar[$key];
     $ra[$key + 5] = $ar[$key];
     $ra[$key + 6] = $ar[$key];
     $ra[$key + 7] = $ar[$key];
     $ra[$key + 8] = $ar[$key];
     $ra[$key + 9] = $ar[$key];
     $ra[$key + 10] = $ar[$key];
     $lval = $ar[$key];
   } 
   //else{
   //  $ra[$key] = $lval;
   //}
 }
 return $ra;
 }
?>
