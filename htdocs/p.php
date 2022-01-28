<?php
$pid = isset($_GET['pid']) ? substr($_GET['pid'], 0, 35) : "";

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

?>
