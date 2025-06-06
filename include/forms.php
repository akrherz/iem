<?php
// Library for doing repetetive forms stuff
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/network.php";

function ugcStateSelect($state, $selected)
{
    $state = substr(strtoupper($state), 0, 2);
    $dbconn = iemdb('postgis');
    $stname = iem_pg_prepare($dbconn, "SELECT ugc, name from ugcs WHERE end_ts is null "
        . " and substr(ugc,1,2) = $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($state));
    $s = "<select name=\"ugc\">\n";
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $z = (substr($row["ugc"], 2, 1) == "Z") ? "Zone" : "County";
        $s .= "<option value=\"" . $row["ugc"] . "\" ";
        if ($row["ugc"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">[" . $row["ugc"] . "] " . $row["name"] . " ($z)</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


/**
 * Select a network type
 * @param nettype the network type
 * @param selected the selected network id
 * @return the select box
 */
function selectNetworkType($nettype, $selected)
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $stname = iem_pg_prepare(
        $dbconn,
        "SELECT * from networks WHERE id ~* $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($nettype));
    $s = "<select class=\"iemselect2\" name=\"network\">\n";
    while ($row = pg_fetch_assoc($rs)) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $row["name"] . "</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


function selectNetwork($selected, $extra = array())
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $rs = pg_exec($dbconn, "SELECT * from networks ORDER by name ASC");
    $s = "<select class=\"iemselect2\" name=\"network\">\n";
    foreach ($extra as $idx => $sid) {
        $s .= "<option value=\"$idx\" ";
        if ($selected == $idx) {
            $s .= "SELECTED";
        }
        $s .= ">[{$idx}] {$sid}</option>\n";
    }
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">[{$row['id']}] {$row['name']}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}

/*
 * Generate a select box that allows multiple selections!
 * @param extra is an array of extra values for this box
 */
function networkMultiSelect(
    $network,
    $selected,
    $extra = array(),
    $label = "station"
) {
    $nt = new NetworkTable($network);
    
    // Create DOM document
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->formatOutput = false; // Keep compact for web output
    
    // Create select element
    $select = $dom->createElement('select');
    $select->setAttribute('name', $label);
    $select->setAttribute('size', '5');
    $select->setAttribute('multiple', 'multiple');

    // Add extra options first
    foreach ($extra as $idx => $sid) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $idx);
        $option->textContent = "[$idx] $sid";
        
        if ($selected == $idx) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }

    // Add options from network table
    foreach ($nt->table as $sid => $tbl) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = "[$sid] " . $tbl["name"];
        
        if ($selected == $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    $dom->appendChild($select);
    return $dom->saveHTML($select);
}

function make_sname($tbl)
{
    // Construct a nice label for the given station
    $dextra = '';
    if (!is_null($tbl['archive_begin'])) {
        $dextra .= sprintf(" [%s-", $tbl["archive_begin"]->format("Y"));
        if (!is_null($tbl['archive_end'])) {
            $dextra .= $tbl["archive_end"]->format("Y");
        }
        $dextra .= "]";
    }
    return sprintf("[%s] %s%s", $tbl['id'], $tbl['name'], $dextra);
}

function networkSelect(
    $network,
    $selected,
    $extra = array(),
    $selectName = "station",
    $only_online = FALSE,
    $clsname = "iemselect2"
) {
    $nt = new NetworkTable($network, FALSE, $only_online);
    
    // Create DOM document
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->formatOutput = false; // Keep compact for web output
    
    // Create select element
    $select = $dom->createElement('select');
    $select->setAttribute('name', $selectName);
    $select->setAttribute('class', $clsname);
    
    // Add options from network table
    foreach ($nt->table as $sid => $tbl) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = make_sname($tbl);
        
        if ($selected === $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    // Add extra options
    foreach ($extra as $idx => $sid) {
        if (is_array($sid)) {
            $tbl = $sid;
            $sid = $idx;
        } else {
            $nt->loadStation($sid);
            $tbl = $nt->table[$sid];
        }
        
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = make_sname($tbl);
        
        if ($selected === $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    $dom->appendChild($select);
    return $dom->saveHTML($select);
}


function networkSelectAuto($network, $selected, $extra = array())
{
    $network = strtoupper($network);
    $s = "";
    $nt = new NetworkTable($network);
    $cities = $nt->table;
    $s .= "<select class=\"iemselect2\" name=\"station\" onChange=\"this.form.submit()\">\n";
    foreach ($cities as $sid => $tbl) {
        $sname = make_sname($tbl);
        if ($tbl["network"] != $network) continue;
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">{$sname}</option>\n";
    }
    foreach ($extra as $idx => $sid) {
        $nt->loadStation($sid);
        $tbl = $nt->table[$sid];
        $sname = make_sname($tbl);
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">{$sname}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}

function rwisMultiSelect($selected, $size)
{
    include_once dirname(__FILE__) . "/network.php";
    $nt = new NetworkTable("IA_RWIS");
    $cities = $nt->table;
    $s = "<select name=\"stations\" size=\"" . $size . "\" MULTIPLE>\n";
    $s .= "<option value=\"_ALL\">Select All</option>\n";
    foreach ($cities as $key => $val) {
        if ($val["network"] != "IA_RWIS") continue;
        $s .= "<option value=\"" . $key . "\"";
        if ($selected == $key) {
            $s .= " SELECTED ";
        }
        $s .= " >" . $val["name"] . " (" . $key . ")\n";
    }

    $s .= "</select>\n";
    return $s;
}


//xss mitigation functions
//https://www.owasp.org/index.php/PHP_Security_Cheat_Sheet#XSS_Cheat_Sheet
function xssafe($data, $encoding = 'UTF-8')
{
    if (is_array($data) || is_null($data)) {
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

// Ensure we get a sane string
function get_str404($name, $default = null, $maxlength = null)
{
    if (!array_key_exists($name, $_REQUEST)) {
        return $default;
    }
    $val = xssafe($_REQUEST[$name]);
    if ($maxlength !== null && strlen($val) > $maxlength) {
        http_response_code(404);
        die();
    }
    return $val;
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
    $showvalue = FALSE,
    $appendbrackets = TRUE,
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
        ($multiple === FALSE || $appendbrackets === FALSE) ? '' : '[]',
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
        "AS" => "American Samoa",
        "AZ" => "Arizona",
        "CA" => "California",
        "CO" => "Colorado",
        "CT" => "Connecticut",
        "DC" => "District of Columbia",
        "DE" => "Delaware",
        "FL" => "Florida",
        "GA" => "Georgia",
        "GU" => "Guam",
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
        "NV" => "Nevada",
        "NH" => "New Hampshire",
        "NJ" => "New Jersey",
        "NM" => "New Mexico",
        "NY" => "New York",
        "NC" => "North Carolina",
        "ND" => "North Dakota",
        "OH" => "Ohio",
        "OK" => "Oklahoma",
        "OR" => "Oregon",
        "PA" => "Pennsylvania",
        "PR" => "Puerto Rico",
        "RI" => "Rhode Island",
        "SC" => "South Carolina",
        "SD" => "South Dakota",
        "TN" => "Tennessee",
        "TX" => "Texas",
        "UT" => "Utah",
        "VT" => "Vermont",
        "VA" => "Virginia",
        "VI" => "Virgin Islands",
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

function wfoSelect($selected)
{
    global $wfos;
    reset($wfos);
    $s = "<select name=\"wfo\" style=\"width: 195px;\">\n";
    foreach ($wfos as $key => $value) {
        $s .= "<option value=\"$key\" ";
        if ($selected == $key) $s .= "SELECTED";
        $s .= ">[" . $key . "] " . $value["city"] . "</option>";
    }
    $s .= "</select>";
    return $s;
}

/* Select minute of the hour */
function minuteSelect($selected, $name, $skip = 1, $jsextra = '')
{
    $s = "<select name=\"{$name}\" {$jsextra}>\n";
    for ($i = 0; $i < 60; $i = $i + $skip) {
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
        $s .= ">" . $ts->format("h A") . "</option>";
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
    $s = "<select name=\"day\">\n";
    for ($k = 1; $k < 32; $k++) {
        $s .= sprintf(
            '<option value="%s"%s>%s</option>',
            $k,
            ($k == intval($selected)) ? " SELECTED" : "",
            $k,
        );
    }
    $s .= "</select>\n";
    return $s;
} // End of daySelect

function daySelect2($selected, $name, $jsextra = '')
{
    $s = "<select name='$name' {$jsextra}>\n";
    for ($k = 1; $k < 32; $k++) {
        $s .= sprintf(
            '<option value="%s"%s>%s</option>',
            $k,
            ($k == intval($selected)) ? " SELECTED" : "",
            $k,
        );
    }
    $s .= "</select>\n";
    return $s;
} // End 
