<?php
$pid = isset($_GET['pid']) ? substr($_GET['pid'], 0, 35) : "";

// 201212100547-KTOP-FXUS63-AFDTOP
$tokens = explode("-", $pid);
if (sizeof($tokens) == 5){
    $url = sprintf("pil=%s&e=%s&bbb=%s", $tokens[3], $tokens[0], $tokens[4]);
} else if (sizeof($tokens) == 4) {
    $url = sprintf("pil=%s&e=%s", $tokens[3], $tokens[0]);
} else {
    http_response_code(404);
    die();
}
header("Location: /wx/afos/p.php?{$url}");

?>
