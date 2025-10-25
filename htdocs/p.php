<?php
require_once "../include/forms.php";
$pid = get_str404('pid', "", 35);
if ($pid != ""){
    // Ensure it is in the proper format
    if (!preg_match("/^[0-9]{12}-[A-Z0-9]{4}-[A-Z0-9]{4,6}-[A-Z\-0-9]{4,10}$/", $pid)){
        xssafe("</script>");
    }
}

// 201212100547-KTOP-FXUS63-AFDTOP
$tokens = explode("-", $pid);
if (sizeof($tokens) == 5){
    $url = sprintf("pil=%s&e=%s&bbb=%s", $tokens[3], $tokens[0], $tokens[4]);
} else if (sizeof($tokens) == 4) {
    $url = sprintf("pil=%s&e=%s", $tokens[3], $tokens[0]);
} else {
    // For whatever reason, we get a lot of social media bots that come here
    // without a pid.  We'll just redirect them to the home page.
    header("Location: /");
    die();
}
header("Location: /wx/afos/p.php?{$url}");
