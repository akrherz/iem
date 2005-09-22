<?php
// PHP Layers Menu 3.1.0 (C) 2001-2003 Marco Pratesi (marco at telug dot it)

/**
* This file contains the code of the ProcessLayersMenu class.
* @package PHPLayersMenu
*/

/**
* This is an extension of the "common" class of the PHP Layers Menu library.
*
* It provides methods useful to process/convert menus data, e.g. to output a menu structure and a DB SQL dump corresponding to already parsed data and hence also to convert a menu structure file to a DB SQL dump and viceversa
*
* @version 3.1.0
* @package PHPLayersMenu
*/
class ProcessLayersMenu extends LayersMenuCommon {

/**
* The constructor method
* @return void
*/
function ProcessLayersMenu() {
	$this->LayersMenuCommon();
}

/**
* Method to output a menu structure corresponding to items of a menu
* @access public
* @param string $menu_name the name of the menu for which a menu structure
*   has to be returned
* @param string $separator the character used in the menu structure format
*   to separate fields of each item
* @return string
*/
function getMenuStructure(
	$menu_name = "",	// non consistent default...
	$separator = "|"
	) {
	$menuStructure = "";
	for ($cnt=$this->_firstItem[$menu_name]; $cnt<=$this->_lastItem[$menu_name]; $cnt++) {	// this counter scans all nodes of the menu
		$menuStructure .= str_repeat(".", $this->tree[$cnt]["level"]);
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["text"];
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["href"];
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["title"];
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["icon"];
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["target"];
		$menuStructure .= $separator;
		$menuStructure .= $this->tree[$cnt]["expanded"];
		$menuStructure .= "\n";
	}
	return $menuStructure;
}

/**
* Method to output a DB SQL dump corresponding to items of a menu
* @access public
* @param string $menu_name the name of the menu for which a DB SQL dump
*   has to be returned
* @return string
*/
function getSQLDump(
	$menu_name = ""	// non consistent default...
	) {
	$SQLDump = "";
	for ($cnt=$this->_firstItem[$menu_name]; $cnt<=$this->_lastItem[$menu_name]; $cnt++) {	// this counter scans all nodes of the menu
		$VALUES = "";
		$SQLDump .= "INSERT INTO ";
		$SQLDump .= $this->tableName;
		$SQLDump .= " (";
		$SQLDump .= $this->tableFields["id"] . ", ";
		$VALUES .= "'" . 10*$cnt . "', ";
		$SQLDump .= $this->tableFields["parent_id"] . ", ";
		if (isset($this->tree[$cnt]["father_node"]) && $this->tree[$cnt]["father_node"] != 0) {
			$VALUES .= "'" . 10*$this->tree[$cnt]["father_node"] . "', ";
		} else {
			$VALUES .= "'1', ";
		}
		$SQLDump .= $this->tableFields["text"] . ", ";
		$VALUES .= "'" . addslashes($this->tree[$cnt]["text"]) . "', ";
		$SQLDump .= $this->tableFields["href"] . ", ";
		$VALUES .= "'" . $this->tree[$cnt]["href"] . "', ";
		if ($this->tableFields["title"] != "''") {
			$SQLDump .= $this->tableFields["title"] . ", ";
			$VALUES .= "'" . addslashes($this->tree[$cnt]["title"]) . "', ";
		}
		if ($this->tableFields["icon"] != "''") {
			$SQLDump .= $this->tableFields["icon"] . ", ";
			$VALUES .= "'" . $this->tree[$cnt]["icon"] . "', ";
		}
		if ($this->tableFields["target"] != "''") {
			$SQLDump .= $this->tableFields["target"] . ", ";
			$VALUES .= "'" . $this->tree[$cnt]["target"] . "', ";
		}
		if ($this->tableFields["orderfield"] != "''") {
			$SQLDump .= $this->tableFields["orderfield"] . ", ";
			$VALUES .= "'" . 10*$cnt . "', ";
		}
		if ($this->tableFields["expanded"] != "''") {
			$SQLDump .= $this->tableFields["expanded"] . ", ";
			$this->tree[$cnt]["expanded"] = (int) $this->tree[$cnt]["expanded"];
			$VALUES .= "'" . $this->tree[$cnt]["expanded"] . "', ";
		}
		$SQLDump = substr($SQLDump, 0, -2);
		$VALUES = substr($VALUES, 0, -2);
		$SQLDump .= ") VALUES (" . $VALUES . ");\n";
	}
	return $SQLDump;
}

} /* END OF CLASS */

?>
