<?php
class Profile {
    function getBasicInfo($userId){
        return array(
            'success'=>true,
            'data'=>array(
                'name'=>'Aaron Conran',
                'company'=>'Ext JS, LLC',
                'email'=>'aaron@extjs.com'
             )
        );
    }
    
    function getPhoneInfo($userId) {
        return array(
            'success'=>true,
            'data'=>array(
                'cell'=>'443-555-1234',
                'office'=>'1-800-CALLEXT',
                'home'=>''
            )
        );
    }

    function getLocationInfo($userId) {
        return array(
            'success'=>true,
            'data'=>array(
                'street'=>'1234 Red Dog Rd.',
                'city'=>'Seminole',
                'state'=>'FL',
                'zip'=>33776
            )
        );
    }}
?>
