<?php
/* Figure out the times of the Satellite Files */
function find_sat($product, $findts)
{
  $a = -1;
  $tdiff = 55012345;
  for($i=0;$i<10;$i++)
  {
    $fs = filemtime("/mesonet/data/gis/images/4326/goes/${product}_${i}.tif");
    $d = abs( $findts - $fs);
    if ($d < $tdiff)
    {
      $a = $i;
      $tdiff = $d;
    } else 
    {
      return $a;
    }
  }
  return $a;
}
?>
