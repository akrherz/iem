<?php

/**
 * Library for doing repetetive forms stuff
 */
//xss mitigation functions
//https://www.owasp.org/index.php/PHP_Security_Cheat_Sheet#XSS_Cheat_Sheet
function xssafe($data, $encoding = 'UTF-8')
{
    if (is_array($data)) {
        return $data;
    }
    $res = htmlspecialchars($data, ENT_QUOTES | ENT_HTML401, $encoding);
    if ($res !== $data) {
        // 404 this
        http_response_code(404);
        die();
    }

    return $res;
}
function xecho($data)
{
    echo xssafe($data);
}

// Ensure we are getting int values from request or we 404
function get_int404($name, $default = null)
{
    if (!array_key_exists($name, $_REQUEST)) {
        return $default;
    }
    $val = $_REQUEST[$name];
    if ($val != "0" && empty($val)) return $default;
    if (!is_numeric($val)) {
        http_response_code(404);
        die();
    }
    return intval($val);
}

// https://stackoverflow.com/questions/834303/startswith-and-endswith-functions-in-php
function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}

function make_checkboxes($name, $selected, $ar)
{
    $myselected = $selected;
    if (!is_array($selected)) {
        $myselected = array($selected);
    }
    $s = "";
    foreach ($ar as $key => $val) {
        $s .= sprintf(
            '<br /><input name="%s" type="checkbox" value="%s" id="%s_%s"%s> ' .
                '<label for="%s_%s">%s</label>' . "\n",
            $name,
            $key,
            $name,
            $key,
            in_array($key, $myselected) ? ' checked="checked"' : "",
            $name,
            $key,
            $val
        );
    }
    return $s;
}

function make_select(
    $name,
    $selected,
    $ar,
    $jscallback = "",
    $cssclass = '',
    $multiple = FALSE,
    $showvalue = FALSE
) {
    // Create a simple HTML select box
    // If multiple, then we arb append [] onto the $name
    $myselected = $selected;
    if (!is_array($selected)) {
        $myselected = array($selected);
    }
    reset($ar);
    $s = sprintf(
        "<select name=\"%s%s\"%s%s%s>\n",
        $name,
        ($multiple === FALSE) ? '' : '[]',
        ($jscallback != "") ? " onChange=\"$jscallback(this.value)\"" : "",
        ($cssclass != "") ? " class=\"$cssclass\"" : "",
        ($multiple === FALSE) ? '' : ' MULTIPLE'
    );
    foreach ($ar as $key => $val) {
        if (is_array($val)) {
            $s .= "<optgroup label=\"$key\">\n";
            foreach ($val as $k2 => $v2) {
                $vv = ($showvalue) ? sprintf("[%s] %s", $k2, $v2) : $v2;
                $s .= sprintf(
                    "<option value=\"%s\"%s>%s</option>\n",
                    $k2,
                    in_array($k2, $myselected) ? " SELECTED" : "",
                    $vv
                );
            }
            $s .= "</optgroup>";
        } else {
            $vv = ($showvalue) ? sprintf("[%s] %s", $key, $val) : $val;
            $s .= sprintf(
                "<option value=\"%s\"%s>%s</option>\n",
                $key,
                in_array($key, $myselected) ? " SELECTED" : "",
                $vv
            );
        }
    }
    $s .= "</select>\n";
    return $s;
}

function stateSelect(
    $selected,
    $jscallback = '',
    $name = 'state',
    $size = 1,
    $multiple = false,
    $all = false
) {
    // Create pull down for selecting a state
    $states = array(
        "AL" => "Alabama",
        "AK" => "Alaska",
        "AR" => "Arkansas",
        "AZ" => "Arizona",
        "CA" => "California",
        "CO" => "Colorado",
        "CT" => "Connecticut",
        "DE" => "Delaware",
        "FL" => "Florida",
        "GA" => "Georgia",
        "HI" => "Hawaii",
        "ID" => "Idaho",
        "IL" => "Illinois",
        "IN" => "Indiana",
        "IA" => "Iowa",
        "KS" => "Kansas",
        "KY" => "Kentucky",
        "LA" => "Louisana",
        "ME" => "Maine",
        "MD" => "Maryland",
        "MA" => "Massachusetts",
        "MI" => "Michigan",
        "MN" => "Minnesota",
        "MS" => "Mississippi",
        "MO" => "Missouri",
        "MT" => "Montana",
        "NE" => "Nebraska",
        "NH" => "New Hampshire",
        "NC" => "North Carolina",
        "ND" => "North Dakota",
        "NV" => "Nevada",
        "NH" => "New Hampshire",
        "NJ" => "New Jersey",
        "NM" => "New Mexico",
        "NY" => "New York",
        "OH" => "Ohio",
        "OK" => "Oklahoma",
        "OR" => "Oregon",
        "PA" => "Pennsylvania",
        "RI" => "Rhode Island",
        "SC" => "South Carolina",
        "SD" => "South Dakota",
        "TN" => "Tennessee",
        "TX" => "Texas",
        "UT" => "Utah",
        "VT" => "Vermont",
        "VA" => "Virginia",
        "WA" => "Washington",
        "WV" => "West Virginia",
        "WI" => "Wisconsin",
        "WY" => "Wyoming",
    );
    $s = sprintf(
        "<select name=\"%s\"%s\n",
        $name,
        ($jscallback != "") ? " onChange=\"$jscallback(this.value)\"" : ""
    );
    if ($size > 1) {
        $s .= ' size="' . $size . '"';
    }
    if ($multiple) {
        $s .= ' MULTIPLE';
    }
    $s .= '>';
    if ($all) {
        $s .= sprintf(
            "<option value=\"_ALL\"%s>All Available</option>",
            ($selected == "_ALL") ? " SELECTED" : ""
        );
    }
    foreach ($states as $key => $val) {
        $s .= "<option value=\"$key\"";
        if ($selected == $key) $s .= " SELECTED";
        $s .= ">[" . $key . "] " . $val . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function vtecPhenoSelect($selected, $name = 'phenomena')
{
    global $vtec_phenomena;
    reset($vtec_phenomena);
    $s = "<select name=\"{$name}\" style=\"width: 195px;\">\n";
    foreach ($vtec_phenomena as $key => $value) {
        $s .= "<option value=\"$key\" ";
        if ($selected == $key) $s .= "SELECTED";
        $s .= ">[" . $key . "] " . $vtec_phenomena[$key] . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function vtecSigSelect($selected, $name = 'significance')
{
    global $vtec_significance;
    reset($vtec_significance);
    $s = "<select name=\"{$name}\" style=\"width: 195px;\">\n";
    foreach ($vtec_significance as $key => $value) {
        $s .= "<option value=\"$key\" ";
        if ($selected == $key) $s .= "SELECTED";
        $s .= ">[" . $key . "] " . $vtec_significance[$key] . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function wfoSelect($selected)
{
    global $wfos;
    reset($wfos);
    $s = "<select name=\"wfo\" style=\"width: 195px;\">\n";
    foreach ($wfos as $key => $value) {
        $s .= "<option value=\"$key\" ";
        if ($selected == $key) $s .= "SELECTED";
        $s .= ">[" . $key . "] " . $wfos[$key]["city"] . "</option>";
    }
    $s .= "</select>";
    return $s;
}

/* Select minute of the hour */
function minuteSelect($selected, $name, $skip = 1)
{
    $s = "<select name='" . $name . "'>\n";
    for ($i = 0; $i < 60; $i = $i + $skip) {
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function minuteSelect2($selected, $name, $jsextra = '')
{
    $s = "<select name='" . $name . "' {$jsextra}>\n";
    for ($i = 0; $i < 60; $i++) {
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}


function hour24Select($selected, $name)
{
    $s = "<select name='" . $name . "'>\n";
    for ($i = 0; $i < 24; $i++) {
        $ts = mktime($i, 0, 0, 1, 1, 0);
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function hourSelect($selected, $name, $jsextra = '')
{
    $s = "<select name=\"{$name}\" {$jsextra}>\n";
    for ($i = 0; $i < 24; $i++) {
        $ts = new DateTime("2000-01-01 $i:00");
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $ts->format("I A") . "</option>";
    }
    return $s . "</select>\n";
}

function gmtHourSelect($selected, $name)
{
    $s = "<select name='" . $name . "'>\n";
    for ($i = 0; $i < 24; $i++) {
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . " UTC</option>";
    }
    return $s . "</select>\n";
}


function monthSelect($selected, $name = "month", $fmt = "M")
{
    $s = "<select name='$name'>\n";
    for ($i = 1; $i <= 12; $i++) {
        $ts = new DateTime("2000-$i-01");
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $ts->format($fmt) . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function yearSelect($start, $selected)
{
    $start = intval($start);
    $now = new DateTime();
    $tyear = $now->format("Y");
    $s = "<select name='year'>\n";
    for ($i = $start; $i <= $tyear; $i++) {
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function yearSelect2($start, $selected, $fname, $jsextra = '', $endyear = null)
{
    $start = intval($start);
    $now = new DateTime();
    $tyear = ($endyear != null) ? $endyear : $now->format("Y");
    $s = "<select name='$fname' {$jsextra}>\n";
    for ($i = $start; $i <= $tyear; $i++) {
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $i . "</option>";
    }
    $s .= "</select>\n";
    return $s;
}

function monthSelect2($selected, $name, $jsextra = '')
{
    $s = "<select name='$name' {$jsextra}>\n";
    for ($i = 1; $i <= 12; $i++) {
        $ts = new DateTime("2000-$i-01");
        $s .= "<option value='" . $i . "' ";
        if ($i == intval($selected)) $s .= "SELECTED";
        $s .= ">" . $ts->format("M") . "</option>";
    }
    return $s . "</select>\n";
}

function daySelect($selected)
{
    $s = "<select name='day'>\n";
    for ($k = 1; $k < 32; $k++) {
        $s .= "<option value=\"" . $k . "\" ";
        if ($k == (int)$selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $k . "</option>";
    }
    $s .= "</select>\n";
    return $s;
} // End of daySelect

function daySelect2($selected, $name, $jsextra = '')
{
    $s = "<select name='$name' {$jsextra}>\n";
    for ($k = 1; $k < 32; $k++) {
        $s .= "<option value=\"" . $k . "\" ";
        if ($k == (int)$selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $k . "</option>";
    }
    $s .= "</select>\n";
    return $s;
} // End 

function segmentSelect($dbconn, $year, $month, $selected, $name = "segid")
{
    $s = "<select name=\"$name\" class=\"iemselect2\">\n";
    $rs = pg_prepare(
        $dbconn,
        "R_S",
        "SELECT segid, major, minor from roads_base "
            . " WHERE archive_begin <= $1 and archive_end > $1 ORDER by major ASC"
    );
    $rs = pg_execute($dbconn, "R_S", array("{$year}-{$month}-01"));
    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $s .= "<option value=\"" . $row["segid"] . "\" ";
        if ($row["segid"] == $selected) $s .= "SELECTED";
        $s .= ">" . $row["major"] . " -- " . $row["minor"] . "</option>";
    }
    return $s;
} // End of segmentSelect
