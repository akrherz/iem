<?php

function printHTML($urls, $width, $height){
    $urls = implode("::", $urls);
return <<<EOF
<form name="jsani" id="jsani" action="#" style="width: {$width}px; height: {$height}px;">
    <input type="hidden" name="filenames" value="{$urls}">
    <input type="hidden" name="controls"
           value="previous, stopplay, next, looprock, slowfast">
    <input type="hidden" name="maxdwell" value="1400">
    <input type="hidden" name="mindwell" value="100">
    <input type="hidden" name="initdwell" value="300">
    <input type="hidden" name="nsteps" value="8">
    <input type="hidden" name="last_frame_pause" value="3"> 
    <input type="hidden" name="first_frame_pause" value="2"> 
    <input type="hidden" name="frame_pause" value="2:4,3:5"> 
</form>
EOF;
}
