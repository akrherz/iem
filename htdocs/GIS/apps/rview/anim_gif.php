<?php
/* Create animated GIF! and then send it to them... */

$fts = isset($_GET["fts"]) ? intval($_GET["fts"]): exit();

chdir("/var/webtmp");

$lines = file($fts .".dat");

$cmdstr = "gifsicle --loopcount=0 --delay=100 -o ${fts}_anim.gif ";
foreach ($lines as $line_num => $line) 
{
  $tokens = split("/", $line);
  $cmdstr .= trim($tokens[sizeof($tokens)-1]) .".gif ";
  $convert = "convert ". trim($tokens[sizeof($tokens)-1]) ." ". trim($tokens[sizeof($tokens)-1]) .".gif";
  `$convert`;
}

`$cmdstr`;

 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=myanimation.gif");

 readfile("${fts}_anim.gif");
?>
