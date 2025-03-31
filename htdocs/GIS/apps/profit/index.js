/* global *, ol */
let map = null;
let player = null;
$(document).ready(() => {
    player = new ol.layer.Tile({
        title: 'Profitability',
        visible: true,
        source: new ol.source.XYZ({
            url: '/c/tile.py/1.0.0/profit2010/{z}/{x}/{y}.png'
        })
    });

    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }), player],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7

        })
    });
    map.addControl(new ol.control.LayerSwitcher());

    $("#yearselect").buttonset();
    $('#yearselect input[type=radio]').change((event) => {
        const year = $(event.target).val();
        player.setSource(new ol.source.XYZ({
            url: `/c/tile.py/1.0.0/profit${year}/{z}/{x}/{y}.png`
        }));
    });
    $("#disclaimer_btn").click(() => {
        $('#disclaimer').dialog({ width: '50%', height: 400 });
    });
});
