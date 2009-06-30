<?php

/**
 * @class Request
 */
class Request {
    public $restful, $method, $controller, $action, $id, $params;
    public function __construct($params) {
        $this->restful = (isset($params["restful"])) ? $params["restful"] : false;
        $this->method = $_SERVER["REQUEST_METHOD"];
        $this->parseRequest();
    }
    public function isRestful() {
        return $this->restful;
    }
    public function to_string() {
        return "controller: " . $this->controller . ', action: ' . $this->action . ', id: ' . $this->id;
    }
    protected function parseRequest() {
        if ($this->method == 'PUT') {   // <-- Have to jump through hoops to get PUT data
            $raw  = '';
            $httpContent = fopen('php://input', 'r');
            while ($kb = fread($httpContent, 1024)) {
                $raw .= $kb;
            }
            fclose($httpContent);
            $params = array();
            parse_str($raw, $params);
            $this->id = (isset($params['id'])) ? $params['id'] : null;
            $this->params = (isset($params['data'])) ? json_decode(stripslashes($params['data']), true) : null;
        } else {
            // grab JSON data if there...
            $this->params = (isset($_REQUEST['data'])) ? json_decode(stripslashes($_REQUEST['data']), true) : null;
            $this->id = (isset($_REQUEST['id'])) ? json_decode(stripslashes($_REQUEST['id']), true) : null;
        }
        // parse path info
        if (isset($_SERVER["PATH_INFO"])){
            $cai = '/^\/([a-z]+\w)\/([a-z]+\w)\/([0-9]+)$/';    // /controller/action/id
            $ca =  '/^\/([a-z]+\w)\/([a-z]+\w)$/';              // /controller/action
            $ci = '/^\/([a-z]+\w)\/([0-9]+)$/';               // /controller/id
            $c =  '/^\/([a-z]+)$/';                             // /controller
            $i =  '/^\/([0-9]+)$/';                             // /id
            $matches = array();
            if (preg_match($cai, $_SERVER["PATH_INFO"], $matches)) {
                $this->controller = $matches[1];
                $this->action = $matches[2];
                $this->id = $matches[3];
            } else if (preg_match($ca, $_SERVER["PATH_INFO"], $matches)) {
                $this->controller = $matches[1];
                $this->action = $matches[2];
            } else if (preg_match($ci, $_SERVER["PATH_INFO"], $matches)) {
                $this->controller = $matches[1];
                $this->id = $matches[2];
            } else if (preg_match($c, $_SERVER["PATH_INFO"], $matches)) {
                $this->controller = $matches[1];
            } else if (preg_match($i, $_SERVER["PATH_INFO"], $matches)) {
                $this->id = $matches[1];
            }
        }
    }
}
?>
