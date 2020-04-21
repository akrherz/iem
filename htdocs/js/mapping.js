
// A Map Widget with a dragable marker that has callbacks
class MapMarkerWidget {

    constructor(mapdiv, lon, lat){
        this.mapdiv = mapdiv;
        this.map;
        this.marker;
        this.callbacks = [];
        var my = this; // closure for below
        this.initialize(lon, lat);
    }

    initialize(lon, lat){
        var latLng = new google.maps.LatLng(lat, lon);
        this.map = new google.maps.Map(document.getElementById(this.mapdiv), {
            zoom: 3,
            center: latLng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        this.marker = new google.maps.Marker({
            position: latLng,
            title: 'Point',
            map: this.map,
            draggable: true
        });
        var my = this;  // closure again
        google.maps.event.addListener(this.marker, 'dragend', function() {
            my.markerCB();
        });
    }

    register(cb){
        this.callbacks.push(cb);
    }
    markerCB(){
        var pos = this.marker.getPosition();
        this.callbacks.forEach(cb => cb(pos.lng(), pos.lat()));
    }
}