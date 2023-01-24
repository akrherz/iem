
// A Map Widget with a dragable marker that has callbacks
var google = window.google || {}; // skipcq: JS-0239

class MapMarkerWidget {

    constructor(mapdiv, lon, lat){
        this.mapdiv = mapdiv;
        this.map = null;
        this.marker = null;
        this.callbacks = [];
        this.initialize(lon, lat);
    }

    initialize(lon, lat){
        const latLng = new google.maps.LatLng(lat, lon);
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
        const my = this;  // closure again
        google.maps.event.addListener(this.marker, 'dragend', () => {
            my.markerCB();
        });
    }

    register(cb){
        this.callbacks.push(cb);
    }
    markerCB(){
        const pos = this.marker.getPosition();
        this.callbacks.forEach(cb => cb(pos.lng(), pos.lat()));
    }
}