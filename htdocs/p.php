<?php

$id = isset($_GET['id']) ? intval($_GET['id']) : "";
$pid = isset($_GET['pid']) ? substr($_GET['pid'],0,32) : "";
if ($id == "" && $pid == "") die();

if ($id != "") {
  die("Sorry, this interface is no longer available!  Please contact us if you need it back!");
} else {
  // 201212100547-KTOP-FXUS63-AFDTOP
  header(sprintf("Location: /wx/afos/p.php?pil=%s&e=%s", 
  	substr($pid,25,6), substr($pid,0,12)));
  exit;
}
?>
