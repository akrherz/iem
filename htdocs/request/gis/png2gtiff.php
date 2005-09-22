<?php
 /* This bad boy converts a PNG to a geo-tiff */

die("Me no workie");

 $pngfp = isset($_GET["png"])? $_GET["png"] : die("None Specified");
 $wrlfile = isset($_GET["wld"]) ? $_GET["wld"] : dir("None Specified");

 if (substr($pngfp,-4,3) != "png") die("Bzzzzt");
 if (substr($wrlfile,-4,3) != "wld") die("Bzzzzt");


 @mkdir("/tmp/png2gtiff");
 chdir("/tmp/png2gtiff");

 $t = explode("/", $pngfp);
 $fn = $t[-1];

 copy($pngfp, $fn);

 $t = explode("/", $wrlfile);
 $fn = $t[-1];

 copy($wrlfile, $fn); 

?>
