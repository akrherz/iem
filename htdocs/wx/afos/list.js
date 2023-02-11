$(document).ready(function(){
    $(".iemselect2").select2();
});

function showHide(v){
    var d2 = document.getElementById("d2");
    if (document.getElementById("drange").checked){
        d2.style.display = "block";
    } else{
        d2.style.display = "none";
    }
}
function j(name){
    $('html,body').animate({
        scrollTop: $("#sect"+name).offset().top
     });
}