<?php
// Library for doing repetetive forms stuff
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/network.php";

/**
 * Generate a UGC (Universal Geographic Code) selection dropdown for a state
 *
 * Creates a select element containing counties and zones for the specified state,
 * fetched from the ugcs database table. Each option displays the UGC code,
 * name, and type (County/Zone).
 *
 * @param string $state Two-letter state code (case-insensitive)
 * @param string $selected Currently selected UGC code
 * @return string Complete HTML select element with UGC options
 *
 * @example Basic usage:
 *   echo ugcStateSelect('IA', 'IAC001');
 *
 * @example With zone selection:
 *   echo ugcStateSelect('mn', 'MNZ001');
 */
function ugcStateSelect($state, $selected)
{
    $state = substr(strtoupper($state), 0, 2);
    $dbconn = iemdb('postgis');
    $stname = iem_pg_prepare($dbconn, "SELECT ugc, name from ugcs WHERE end_ts is null "
        . " and substr(ugc,1,2) = $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($state));

    // Build options array from database results
    $options = array();
    while ($row = pg_fetch_assoc($rs)) {
        $z = (substr($row["ugc"], 2, 1) == "Z") ? "Zone" : "County";
        $options[$row["ugc"]] = "[" . $row["ugc"] . "] " . $row["name"] . " ($z)";
    }

    return make_select("ugc", $selected, $options);
}


/**
 * Select a network type
 * @param string $nettype the network type pattern to match
 * @param string $selected the selected network id
 * @return string the select box HTML
 */
function selectNetworkType($nettype, $selected)
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $stname = iem_pg_prepare(
        $dbconn,
        "SELECT * from networks WHERE id ~* $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($nettype));

    // Build options array from database results
    $options = array();
    while ($row = pg_fetch_assoc($rs)) {
        $options[$row["id"]] = $row["name"];
    }

    return make_select("network", $selected, $options, "", "iemselect2");
}


/**
 * Create a network selection dropdown
 *
 * Generates a select element containing all available networks from the database,
 * with optional extra options. Uses the modernized make_select function for
 * proper HTML generation and escaping.
 *
 * @param string $selected The currently selected network ID (case-insensitive)
 * @param array $extra Additional options to include at the top of the list.
 *                     Array keys are option values, array values are option labels
 * @return string Complete HTML select element with network options
 *
 * @example Basic usage:
 *   echo selectNetwork('IA_ASOS');
 *
 * @example With extra options:
 *   $extras = array('_ALL_' => 'All Networks', 'CUSTOM' => 'Custom Selection');
 *   echo selectNetwork('IA_ASOS', $extras);
 */
function selectNetwork($selected, $extra = array())
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $rs = pg_query($dbconn, "SELECT * from networks ORDER by name ASC");

    // Build options array starting with extra options
    $options = array();
    foreach ($extra as $idx => $sid) {
        $options[$idx] = "[{$idx}] {$sid}";
    }

    // Add database results to options array
    while ($row = pg_fetch_assoc($rs)) {
        $options[$row["id"]] = "[{$row['id']}] {$row['name']}";
    }

    return make_select("network", $selected, $options, "", "iemselect2");
}

/**
 * Generate a multiple selection box for network stations
 *
 * Creates a select element with multiple selection capability containing
 * network stations and optional extra entries.
 *
 * @param string|array $network Network identifier(s)
 * @param string $selected Currently selected value
 * @param array $extra Additional options to include (key => value pairs)
 * @param string $label Name attribute for the select element
 * @return string HTML select element with multiple selection enabled
 */
function networkMultiSelect(
    $network,
    $selected,
    $extra = array(),
    $label = "station"
) {
    $nt = new NetworkTable($network);
    $options = array();

    // Add extra options first
    foreach ($extra as $idx => $sid) {
        $options[$idx] = "[$idx] $sid";
    }

    // Add options from network table
    foreach ($nt->table as $sid => $tbl) {
        $options[$sid] = "[$sid] " . $tbl["name"];
    }

    // Use standardized make_select with multiple selection and size attributes
    return make_select(
        $label,           // name
        $selected,        // selected value
        $options,         // options array
        "",               // jscallback
        "",               // cssclass
        TRUE,             // multiple
        FALSE,            // showvalue
        TRUE,             // appendbrackets
        array('size' => 5) // extra attributes for size
    );
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
    $clsname = "iemselect2",
    $size = 1,
) {
    $nt = new NetworkTable($network, FALSE, $only_online);

    // Build options array from network table
    $options = array();
    foreach ($nt->table as $sid => $tbl) {
        $options[$sid] = make_sname($tbl);
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
        $options[$sid] = make_sname($tbl);
    }

    return make_select(
        $selectName,
        $selected,
        $options,
        "",
        $clsname,
        FALSE,          // multiple selection
        FALSE,          // showvalue
        FALSE,          // appendbrackets
        array('size' => $size) // extra attributes for size
    );
}


/**
 * Generate a network station selection dropdown with auto-submit on change
 *
 * Creates a select element for stations within a specific network that
 * automatically submits the form when selection changes. Includes support
 * for extra station entries.
 *
 * @param string $network Network identifier (case-insensitive)
 * @param string $selected Currently selected station ID
 * @param array $extra Additional station entries to include (station_id => value pairs)
 * @return string Complete HTML select element with auto-submit functionality
 *
 * @example Basic usage:
 *   echo networkSelectAuto('IA_ASOS', 'KAMW');
 *
 * @example With extra stations:
 *   $extras = array('CUSTOM1' => 'Custom Station 1');
 *   echo networkSelectAuto('IA_ASOS', 'KAMW', $extras);
 */
function networkSelectAuto($network, $selected, $extra = array())
{
    $network = strtoupper($network);
    $nt = new NetworkTable($network);
    $cities = $nt->table;

    // Build options array from network table
    $options = array();
    foreach ($cities as $sid => $tbl) {
        if ($tbl["network"] != $network) continue;
        $sname = make_sname($tbl);
        $options[$sid] = $sname;
    }

    // Add extra station entries
    foreach ($extra as $idx => $sid) {
        $nt->loadStation($sid);
        $tbl = $nt->table[$sid];
        $sname = make_sname($tbl);
        $options[$sid] = $sname;
    }
    return make_select(
        "station",                    // name
        $selected,                   // selected value
        $options,                    // options array
        null,                        // onchange callback
        "iemselect2",               // CSS class
        FALSE,                      // multiple
        FALSE,                      // showvalue
        FALSE,                      // appendbrackets
        array('style' => 'min-width: 300px;') // extra attributes for width
    );
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
        // 405, which ends up hitting some iemwebfarm code
        http_response_code(405);
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
        // passed up to iemwebfarm handler
        http_response_code(405);
        die();
    }
    return $val;
}

// Ensure we are getting int values from request or we 405
function get_int404($name, $default = null)
{
    if (!array_key_exists($name, $_REQUEST)) {
        return $default;
    }
    $val = $_REQUEST[$name];
    if ($val != "0" && empty($val)) return $default;
    if (!is_numeric($val)) {
        // passed up to iemwebfarm handler
        http_response_code(405);
        die();
    }
    return intval($val);
}

// Ensure we are getting float values from request or we 405
function get_float404($name, $default = null)
{
    if (!array_key_exists($name, $_REQUEST)) {
        return $default;
    }
    $val = $_REQUEST[$name];
    if ($val != "0" && empty($val)) return $default;
    if (!is_numeric($val)) {
        // passed up to iemwebfarm handler
        http_response_code(405);
        die();
    }
    return floatval($val);
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

/**
 * Create a HTML select element with options using modern DOM generation
 *
 * This function generates a complete HTML select element with proper escaping
 * and attribute handling. Supports single/multiple selection, optgroups,
 * JavaScript callbacks, and CSS styling.
 *
 * @param string $name The name attribute for the select element
 * @param string|array $selected The selected value(s). Can be a single value
 *                               or array for multiple selections
 * @param array $ar The options array. Simple key=>value pairs create options.
 *                  Nested arrays create optgroups with the key as group label
 * @param string $jscallback Optional JavaScript function name to call on change.
 *                           Will be called with selected value as parameter
 * @param string $cssclass Optional CSS class(es) to add to the select element
 * @param bool $multiple Whether to allow multiple selections (adds 'multiple' attribute)
 * @param bool $showvalue Whether to display option values in brackets before labels
 * @param bool $appendbrackets Whether to append '[]' to name for multiple selects
 * @param array $extraAttrs Optional additional HTML attributes as key=>value pairs
 *
 * @return string Complete HTML select element as string
 *
 * @example Basic usage:
 *   $options = array('val1' => 'Label 1', 'val2' => 'Label 2');
 *   echo make_select('myselect', 'val1', $options);
 *
 * @example With optgroups:
 *   $options = array(
 *       'Group 1' => array('g1v1' => 'Group 1 Value 1'),
 *       'Group 2' => array('g2v1' => 'Group 2 Value 1')
 *   );
 *   echo make_select('grouped', 'g1v1', $options);
 *
 * @example Multiple selection with callback:
 *   echo make_select('multi', array('val1', 'val3'), $options,
 *                    'handleChange', 'form-control', TRUE);
 */
function make_select(
    $name,
    $selected,
    $ar,
    $jscallback = "",
    $cssclass = '',
    $multiple = FALSE,
    $showvalue = FALSE,
    $appendbrackets = TRUE,
    $extraAttrs = array()
) {
    // Create a simple HTML select box using DOMDocument
    $myselected = $selected;
    if (!is_array($selected)) {
        $myselected = array($selected);
    }

    // Create DOM document
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->formatOutput = false; // Keep compact for web output

    // Create select element
    $select = $dom->createElement('select');

    // Set name attribute with optional brackets for multiple selection
    $nameAttr = $name;
    if ($multiple !== FALSE && $appendbrackets !== FALSE) {
        $nameAttr .= '[]';
    }
    $select->setAttribute('name', $nameAttr);

    // Set additional attributes
    if ($jscallback !== "") {
        $select->setAttribute('onChange', $jscallback . '(this.value)');
    }
    if ($cssclass !== '') {
        $select->setAttribute('class', $cssclass);
    }
    if ($multiple !== FALSE) {
        $select->setAttribute('multiple', 'multiple');
    }

    // Set any extra attributes
    foreach ($extraAttrs as $attr => $value) {
        $select->setAttribute($attr, $value);
    }

    // Process array options
    foreach ($ar as $key => $val) {
        if (is_array($val)) {
            // Create optgroup for nested arrays
            $optgroup = $dom->createElement('optgroup');
            $optgroup->setAttribute('label', $key);

            foreach ($val as $k2 => $v2) {
                $option = $dom->createElement('option');
                $option->setAttribute('value', $k2);

                $displayText = $showvalue ? "[$k2] $v2" : $v2;
                $option->textContent = $displayText;

                if (in_array($k2, $myselected)) {
                    $option->setAttribute('selected', 'selected');
                }

                $optgroup->appendChild($option);
            }

            $select->appendChild($optgroup);
        } else {
            // Create regular option
            $option = $dom->createElement('option');
            $option->setAttribute('value', $key);

            $displayText = $showvalue ? "[$key] $val" : $val;
            $option->textContent = $displayText;

            if (in_array($key, $myselected)) {
                $option->setAttribute('selected', 'selected');
            }

            $select->appendChild($option);
        }
    }

    $dom->appendChild($select);
    return $dom->saveHTML($select);
}

/**
 * Generate a US state and territory selection dropdown
 *
 * Creates a select element containing all US states, territories, and districts.
 * Each option displays the state code and full name. Optionally includes an
 * "All Available" option. Uses the standardized make_select() function.
 *
 * @param string $selected Currently selected state code
 * @param string $jscallback JavaScript function to call on change (optional)
 * @param string $name HTML name attribute for the select element
 * @param int $size Number of visible options (HTML size attribute)
 * @param bool $multiple Whether to allow multiple selections
 * @param bool $all Whether to include "All Available" option at top
 * @return string Complete HTML select element with state options
 *
 * @example Basic usage:
 *   echo stateSelect('IA');  // Iowa selected
 * @example With callback:
 *   echo stateSelect('CA', 'updateDisplay', 'state_code', 5, true, true);
 */
function stateSelect(
    $selected,
    $jscallback = '',
    $name = 'state',
    $size = 1,
    $multiple = false,
    $all = false
) {
    // US states, territories, and districts
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

    // Build options array
    $options = array();
    if ($all) {
        $options["_ALL"] = "All Available";
    }

    foreach ($states as $key => $val) {
        $options[$key] = "[$key] $val";
    }

    // Additional attributes for size
    $extraAttrs = array();
    if ($size > 1) {
        $extraAttrs['size'] = $size;
    }

    return make_select(
        $name,
        $selected,
        $options,
        $jscallback,
        '',        // cssclass
        $multiple,
        FALSE,     // showvalue (options are already formatted with [CODE])
        FALSE,     // appendbrackets (let caller control name format)
        $extraAttrs
    );
}

/**
 * Generate a Weather Forecast Office (WFO) selection dropdown
 *
 * Creates a select element containing all Weather Forecast Offices using
 * the global $wfos array. Each option displays the WFO code and city name.
 * Uses the standardized make_select() function for consistency.
 *
 * @param string $selected Currently selected WFO code
 * @return string Complete HTML select element with WFO options
 *
 * @example Basic usage:
 *   echo wfoSelect('DMX');  // Des Moines WFO
 */
function wfoSelect($selected)
{
    global $wfos;
    reset($wfos);

    // Build options array from global $wfos
    $options = array();
    foreach ($wfos as $key => $value) {
        $options[$key] = "[$key] " . $value["city"];
    }

    return make_select(
        'wfo',           // name
        $selected,       // selected value
        $options         // options array
    );
}

/**
 * Generate a minute selection dropdown with custom interval
 *
 * Creates a select element for selecting minutes with customizable skip interval.
 * Supports JavaScript/HTML attributes for enhanced functionality.
 * Uses the standardized make_select() function for consistency.
 *
 * @param int $selected Currently selected minute value (0-59)
 * @param string $name Name attribute for the select element
 * @param int $skip Interval between minute options (default: 1)
 * @return string Complete HTML select element with minute options
 *
 * @example Basic usage:
 *   echo minuteSelect(30, 'start_minute');  // 30 selected, every minute
 * @example With 5-minute intervals:
 *   echo minuteSelect(15, 'minute', 5);  // 15 selected, 5-minute intervals
 * @example With JavaScript:
 *   echo minuteSelect(0, 'minute', 1, 'onchange="updateTime()"');
 */
function minuteSelect($selected, $name, $skip = 1)
{
    // Build options array with skip interval
    $options = array();
    for ($i = 0; $i < 60; $i = $i + $skip) {
        $options[$i] = (string)$i;
    }

    return make_select(
        $name,          // name
        $selected,      // selected value
        $options,       // options array
    );
}


/**
 * Generate a 24-hour selection dropdown (0-23)
 *
 * Creates a select element for selecting hours of the day in 24-hour format.
 * Uses the standardized make_select() function for consistency.
 *
 * @param int $selected Currently selected hour value (0-23)
 * @param string $name Name attribute for the select element
 * @return string Complete HTML select element with 24-hour options
 *
 * @example Basic usage:
 *   echo hour24Select(14, 'start_hour');  // 14 (2 PM) selected
 */
function hour24Select($selected, $name)
{
    // Build options array for 24-hour format (0-23)
    $options = array();
    for ($i = 0; $i < 24; $i++) {
        $options[$i] = (string)$i;
    }

    return make_select(
        $name,      // name
        $selected,  // selected value
        $options    // options array
    );
}

/**
 * Generate a 12-hour format hour selection dropdown with AM/PM
 *
 * Creates a select element for selecting hours of the day in 12-hour format
 * with AM/PM display. Uses the standardized make_select() function with support
 * for additional JavaScript attributes via $extraAttrs.
 *
 * @param int $selected Currently selected hour value (0-23)
 * @param string $name Name attribute for the select element
 * @return string Complete HTML select element with 12-hour format options
 *
 * @example Basic usage:
 *   echo hourSelect(14, 'hour');  // 2 PM selected
 */
function hourSelect($selected, $name)
{
    // Build options array for 12-hour format with AM/PM
    $options = array();
    for ($i = 0; $i < 24; $i++) {
        $ts = new DateTime("2000-01-01 $i:00");
        $options[$i] = $ts->format("h A");
    }

    return make_select(
        $name,          // name
        $selected,      // selected value
        $options,       // options array
    );
}

/**
 * Generate a GMT/UTC hour selection dropdown (0-23)
 *
 * Creates a select element for selecting hours of the day in 24-hour GMT/UTC format.
 * Each option displays the hour followed by "UTC" (e.g., "0 UTC", "14 UTC").
 * Uses the standardized make_select() function for consistency.
 *
 * @param int $selected Currently selected hour value (0-23)
 * @param string $name Name attribute for the select element
 * @return string Complete HTML select element with GMT/UTC hour options
 *
 * @example Basic usage:
 *   echo gmtHourSelect(14, 'gmt_hour');  // 14 UTC selected
 * @example With custom name:
 *   echo gmtHourSelect(0, 'start_hour_utc');  // 0 UTC selected
 */
function gmtHourSelect($selected, $name)
{
    // Build options array for 24-hour GMT/UTC format
    $options = array();
    for ($i = 0; $i < 24; $i++) {
        $options[$i] = $i . " UTC";
    }

    return make_select(
        $name,      // name
        $selected,  // selected value
        $options    // options array
    );
}


/**
 * Generate a month selection dropdown with customizable format
 *
 * Creates a select element for selecting months using customizable date format.
 * Supports custom name attributes, date formatting, and JavaScript/HTML attributes.
 * Uses the standardized make_select() function for consistency.
 *
 * @param int $selected Currently selected month value (1-12)
 * @param string $name Name attribute for the select element (default: "month")
 * @param string $fmt Date format for month display (default: "M" for 3-letter abbreviation)
 * @param string $jsextra Additional JavaScript/HTML attributes (default: "")
 * @return string Complete HTML select element with month options
 *
 * @example Basic usage (backwards compatible):
 *   echo monthSelect(6);  // June selected, name="month", format="M"
 * @example Custom name and format:
 *   echo monthSelect(3, 'birth_month', 'F');  // Full month name
 * @example With JavaScript:
 *   echo monthSelect(12, 'month', 'M', 'onchange="updateDays()"');
 */
function monthSelect($selected, $name = "month", $fmt = "M", $jsextra = '')
{
    // Build options array for months (1-12) with specified format
    $options = array();
    for ($i = 1; $i <= 12; $i++) {
        $ts = new DateTime("2000-$i-01");
        $options[$i] = $ts->format($fmt);
    }

    // Parse jsextra for additional attributes
    $extraAttrs = array();
    $jscallback = '';
    $cssclass = '';

    if (!empty($jsextra)) {
        // Parse onchange callback
        if (preg_match('/onchange\s*=\s*["\']([^"\']*)["\']/', $jsextra, $matches)) {
            $jscallback = $matches[1];
        }
    }

    return make_select(
        $name,          // name
        $selected,      // selected value
        $options,       // options array
        $jscallback,    // JavaScript callback
        $cssclass,      // CSS class
        FALSE,          // multiple
        FALSE,          // showvalue
        FALSE,          // appendbrackets
        $extraAttrs     // extra attributes
    );
}

/**
 * Generate a year selection dropdown from start year to end year
 *
 * Creates a select element for selecting years from a specified start year
 * up to an end year (defaults to current year). Supports custom name attributes
 * and JavaScript/HTML attributes. Uses the standardized make_select() function.
 *
 * @param int $start Starting year for the range
 * @param int $selected Currently selected year value
 * @param string $fname Name attribute for the select element (default: "year")
 * @param string $jsextra Additional JavaScript/HTML attributes (default: "")
 * @param int|null $endyear Ending year for the range (default: current year)
 * @return string Complete HTML select element with year options
 *
 * @example Basic usage (backwards compatible):
 *   echo yearSelect(2000, 2023);  // Years 2000-current, 2023 selected, name="year"
 * @example Custom name and end year:
 *   echo yearSelect(1950, 1995, 'birth_year', '', 2000);  // Years 1950-2000
 * @example With JavaScript:
 *   echo yearSelect(2010, 2020, 'start_year', 'onchange="updateRange()"');
 */
function yearSelect($start, $selected, $fname = 'year', $jsextra = '', $endyear = null)
{
    $start = intval($start);
    $now = new DateTime();
    $tyear = ($endyear !== null) ? intval($endyear) : intval($now->format("Y"));

    // Build options array for year range
    $options = array();
    for ($i = $start; $i <= $tyear; $i++) {
        $options[$i] = (string)$i;
    }

    // Parse jsextra for additional attributes
    $extraAttrs = array();
    $jscallback = '';
    $cssclass = '';

    if (!empty($jsextra)) {
        // Parse onchange callback
        if (preg_match('/onchange\s*=\s*["\']([^"\']*)["\']/', $jsextra, $matches)) {
            $jscallback = $matches[1];
        }
    }

    return make_select(
        $fname,         // name
        $selected,      // selected value
        $options,       // options array
        $jscallback,    // JavaScript callback
        $cssclass,      // CSS class
        FALSE,          // multiple
        FALSE,          // showvalue
        FALSE,          // appendbrackets
        $extraAttrs     // extra attributes
    );
}

/**
 * Generate a day selection dropdown (1-31)
 *
 * Creates a select element for selecting day of month from 1 to 31.
 * Supports custom name attributes and JavaScript/HTML attributes for enhanced functionality.
 * Uses the standardized make_select() function for consistency.
 *
 * @param int $selected Currently selected day value (1-31)
 * @param string $name Name attribute for the select element (default: "day")
 * @return string Complete HTML select element with day options
 *
 * @example Basic usage (backwards compatible):
 *   echo daySelect(15);  // Day 15 selected, name="day"
 * @example Custom name:
 *   echo daySelect(20, 'birth_day');  // Day 20 selected, name="birth_day"
 */
function daySelect($selected, $name = 'day')
{
    // Build options array for days 1-31
    $options = array();
    for ($k = 1; $k < 32; $k++) {
        $options[$k] = (string)$k;
    }

    return make_select(
        $name,          // name
        $selected,      // selected value
        $options,       // options array
    );
} // End of daySelect


