<?php // content="text/plain; charset=utf-8"

include "jpgraph/jpgraph.php";
include "jpgraph/jpgraph_led.php";

// By default each "LED" circle has a radius of 3 pixels. Change to 5 and slghtly smaller margin
$led = new DigitalLED74(6);
$led->SetSupersampling(2);
$led->StrokeNumber('123.',LEDC_RED);



?>
