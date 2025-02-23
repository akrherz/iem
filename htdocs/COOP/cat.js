// ES Module
import $ from '/js/jquery.module.js';

let currentmode = true;

function hiderows(){
    if (currentmode){
        $('tr.nodata').hide();
        $("#rowshower").attr('value','Show rows without data');
    } else {
        $('tr.nodata').show();
        $("#rowshower").attr('value','Hide rows without data');
    }
    currentmode = !currentmode;
}

$(document).ready(() => {
    $("#rowshower").click(hiderows);
});