<?php
/*
 * Facebook call's back to this so that I can take action on comments
 */
include("../config/settings.inc.php");
include("Zend/Mail.php");


 
 $mail = new Zend_Mail();
 $mail->setBodyText(print_r($_REQUEST, TRUE));
 $mail->setSubject("IEM Facebook Comment");
 $mail->setFrom("mesonet@mesonet.agron.iastate.edu", 'IEM Website');
 $mail->addTo("akrherz@iastate.edu");
 $mail->send();

?>