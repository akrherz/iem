/* global CONFIG */

//callback on when the marker is done moving    		
function displayCoordinates(pnt) {
    const lat = pnt.lat().toFixed(8);
    const lng = pnt.lng().toFixed(8);
    $("#newlat").val(lat);
    $("#newlon").val(lng);
}

// eslint-disable-next-line no-unused-vars
function load() { // skipcq: JS-0128
    const mapOptions = {
        zoom: 15,
        center: new google.maps.LatLng(CONFIG.lat, CONFIG.lon),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    const map = new google.maps.Map(document.getElementById('mymap'),
        mapOptions);
    const marker = new google.maps.Marker({
        position: mapOptions.center,
        map,
        draggable: true
    });
    google.maps.event.addListener(marker, 'dragend', () => {
        displayCoordinates(marker.getPosition());
    });
}
