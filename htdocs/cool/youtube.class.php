<?php

error_reporting(E_ALL);



// for pagination

session_start();



////////////////////////////////////////

// youtube.class.php v1.0 /////////

// released 3/8/2007 ///////////////

// for waxjelly.wordpress.com ////

// the internet is for users ////////

////////////////////////////////////////

// this class is to be used free ////

// of charge so long as this line //

// remains intact, and untouched/

////////////////////////////////////////

define('API_KEY', 'Rfr3ThLl-NY'); // YOUR YOUTUBE DEVELOPERS API KEY

//-------------------------------//

// DO NOT EDIT

//-------------------------------//

/////////////////////

// CONSTANTS //

////////////////////

define('API_URL', 'http://www.youtube.com/');



// CALL GATEWAYS

define('API_REST_CALL', API_URL . 'api2_rest?');

define('API_XMLRPC_CALL', API_URL . 'api2_xmlrpc?');

 

// METHODS FOR VIDEOS

define('BY_TAG', 'list_by_tag');
define('BY_USER', 'list_by_user');


class XmlToArray
{
    
    var $xml='';
    
    /**
    * Default Constructor
    * @param $xml = xml data
    * @return none
    */
    
    function XmlToArray($xml)
    {
       $this->xml = $xml;    
    }
    
    /**
    * _struct_to_array($values, &$i)
    *
    * This is adds the contents of the return xml into the array for easier processing.
    * Recursive, Static
    *
    * @access    private
    * @param    array  $values this is the xml data in an array
    * @param    int    $i  this is the current location in the array
    * @return    Array
    */
    
    function _struct_to_array($values, &$i)
    {
        $child = array();
        if (isset($values[$i]['value'])) array_push($child, $values[$i]['value']);
        
        while ($i++ < count($values)) {
            switch ($values[$i]['type']) {
                case 'cdata':
                array_push($child, $values[$i]['value']);
                break;
                
                case 'complete':
                    $name = $values[$i]['tag'];
                    if(!empty($name)){
                    $child[$name]= ($values[$i]['value'])?($values[$i]['value']):'';
                    if(isset($values[$i]['attributes'])) {                    
                        $child[$name] = $values[$i]['attributes'];
                    }
                }    
              break;
                
                case 'open':
                    $name = $values[$i]['tag'];
                    $size = isset($child[$name]) ? sizeof($child[$name]) : 0;
                    $child[$name][$size] = $this->_struct_to_array($values, $i);
                break;
                
                case 'close':
                return $child;
                break;
            }
        }
        return $child;
    }//_struct_to_array
    
    /**
    * createArray($data)
    *
    * This is adds the contents of the return xml into the array for easier processing.
    *
    * @access    public
    * @param    string    $data this is the string of the xml data
    * @return    Array
    */
    function createArray()
    {
        $xml    = $this->xml;
        $values = array();
        $index  = array();
        $array  = array();
        $parser = xml_parser_create();
        xml_parser_set_option($parser, XML_OPTION_SKIP_WHITE, 1);
        xml_parser_set_option($parser, XML_OPTION_CASE_FOLDING, 0);
        xml_parse_into_struct($parser, $xml, $values, $index);
        xml_parser_free($parser);
        $i = 0;
        $name = $values[$i]['tag'];
        $array[$name] = isset($values[$i]['attributes']) ? $values[$i]['attributes'] : '';
        $array[$name] = $this->_struct_to_array($values, $i);
        return $array;
    }//createArray
}



// create youtube class

class youtube {

	// CLASS PROPERTIES

	

	// VARIABLE TO HOLD THE SIMPLE XML ELEMENT WITH RETURNED DATA

	var $xml;

	// HOLDS CONFIG OPTIONS

	var  $config = array();

	// VAR TO STORE THE QUERY STRING FOR YOUTUBE

	var $api_call;

	// RETURNED DATA FROM XML CALL

	var $return;

	var $tag;

	// IF WE ENCOUNTER ERRORS ALONG OUR JOURNEY

	var $errors;



	// CONSTRUCTION VARIABLES

	function youtube($api_key = API_KEY, $page = 1, $per_page = 25) {

		// JUST TO SETUP SOME DEFAULT VALUES FOR A NOMINAL CALL.

		// WE WANTED TO MAKE IT EASY TO JUST USE THE CLASS, NOT CONFIGURE IT.

		$this->set('api_key', API_KEY);

		$this->set('page', $page);

		$this->set('per_page', $per_page);



		// modify the call

		$this->modify_call(API_REST_CALL . 'method=youtube.');

	}



	function xml_to_array($xml) {

		$fils = 0;

		$tab = false;

		$array = array();



		foreach($xml->children() as $key => $value) {

			$child = $this->xml_to_array($value);



			//To deal with the attributes

			//foreach ($node->attributes() as $ak => $av) {

			//	$child[$ak] = (string)$av;

			//}

			//Let see if the new child is not in the array

			if ($tab == false && in_array($key, array_keys($array))) {

				//If this element is already in the array we will create an indexed array

				$tmp = $array[$key];

				$array[$key] = NULL;

				$array[$key][] = $tmp;

				$array[$key][] = $child;

				$tab = true;

			} elseif($tab == true) {

				//Add an element in an existing array

				$array[$key][] = $child;

			} else {

				//Add a simple element

				$array[$key] = $child;

			}

			$fils++;

		}



		if($fils==0) {

			return (string)$xml;

		}

		return $array;

	}



	// SET A CONFIG VARIABLE

	 function set($item, $value) {

		$this->config[$item] = $value;

	}



	// ACCESS CONFIG

	 function config($item) {

		return $this->config[$item];

	}



	// MODIFY THE CALL CLASS PROPERTY

	 function modify_call($params) {

		$this->api_call .= $params;

	}



	// ECHO THE CALL FOR DEBUGGING

	 function return_call() {

		return $this->api_call;

	}



	// YOUTUBE VIDEO METHODS

	 function videos($data = 'zombie', $method = BY_USER) {

		//---------------------------------------------//

		$this->api_call .= 'videos.'; ///////////////////////

		//---------------------------------------------//

		switch ($method) {

			case BY_TAG:
				$this->tag = '&tag='. $data;
				$this->modify_call($method . '&dev_id=' . $this->config['api_key'] . $this->tag);
				break;
			case BY_USER:
				$this->tag = '&user='. $data;
				$this->modify_call($method . '&dev_id=' . $this->config['api_key'] . $this->tag);
				break;



			default:

				return 'The WaxJelly YouTube API Class only supports retrieving videos by tag.';

				break;

		}



		// CALL DISPLAY

		return $this->display();

	}



	 function tags_for_video($tags) {

		$tag_links = '';



		// explode

		$x = explode(' ', $tags);

		if (count($x) > 0) {

			foreach ($x as $k => $v) {

				$tag_links .= "<a href=\"{$_SERVER['PHP_SELF']}?tag=$v\">$v</a> ";

			}

		} else { 

			$tag_links = "<a href=\"{$_SERVER['PHP_SELF']}?tag=zombie\">zombie</a>";

		}

		return $tag_links;

	}



	// DISPLAY RESULTS

	 function display() {

		// CHECK FOR A NEW PAGE & PER PAGE

		if (isset($_GET['page'])) {

			$this->set('page', $_GET['page']);

		}

		if (isset($_GET['per_page'])) {

			$this->set('per_page', $_GET['per_page']);

		}



		// per page, page, prev, next

		// total videos, total pages

		$this->modify_call('&page=' . $this->config('page') . '&per_page=' . $this->config('per_page'));



		// SEND REQUEST

		$this->return = file_get_contents($this->return_call());

		$xmlx = new XmlToArray($this->return);

		$this->xml = $xmlx->createArray();
		$this->xml = $this->xml['ut_response'];
		/*
		echo '<pre>';
		print_r($this->xml);
		echo '</pre>';
*/
		// CHECK IF THEY'RE ASKING FOR A VIDEO ID

		if (isset($_GET['video_id'])) {

			define('YOUTUBE_VIDEO_ID', $_GET['video_id']);

			

			// loop through videos to get videos index

			foreach ($this->xml['video_list'][0]['video'] as $indx => $array) {

				if ($array['id'] == $_GET['video_id']) {

					$index = $indx;

					break;

				} else {

				   $index = $indx;

				}

			}



			// define index

			define('YOUTUBE_VIDEO_INDEX', $index);

		} else {

			define('YOUTUBE_VIDEO_ID', $this->xml['video_list'][0]['video'][0]['id']);

			define('YOUTUBE_VIDEO_INDEX', 0);

		}



		//////////////////////////////////////////

		// CREATE DISPLAY CONSTANTS //

		/////////////////////////////////////////

		define('YOUTUBE_PAGE', $this->config('page'));

		define('YOUTUBE_PER_PAGE', $this->config('per_page'));

		$prev = ($this->config('page') - 1 == 0) ? 1 : $this->config('page') - 1;

		define('YOUTUBE_PREV_PAGE', $prev . $this->tag);

		define('YOUTUBE_NEXT_PAGE', $this->config('page') + 1 . $this->tag);

		define('YOUTUBE_TOTAL_VIDEOS', $this->xml['video_list'][0]['total']);

		define('YOUTUBE_TOTAL_PAGES', ceil($this->xml['video_list'][0]['total'] / $this->config('per_page')));



		// CONVERT FROM SIMPLEXML OBJECT TO ARRAY

		return $this->xml;

	}

}


//////////functions //////////////////

?>
