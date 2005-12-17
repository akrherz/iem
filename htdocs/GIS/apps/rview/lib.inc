<?php
/* Figure out the times of the Satellite Files */
function find_sat($product, $findts)
{
  $a = -1;
  $tdiff = 55012345;
  $basets = filemtime("/mesonet/data/gis/images/4326/goes/${product}_0.tif");
  for($i=0;$i<10;$i++)
  {
    $fs = $basets - ($i * 30 * 60);
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
  if ($a == 9) return -1;
  return $a;
}
?>
