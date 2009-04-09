
Ext.onReady(function(){
    var map, slight_vector, moderate_layer, high_vector, controls;

    var map = new OpenLayers.Map();
    var wms = new OpenLayers.Layer.WMS(
        "OpenLayers WMS",
        "http://labs.metacarta.com/wms/vmap0?",
        {layers: 'basic'}
    );


    
  //OpenLayers.Feature.Vector.style['default']['strokeWidth'] = '2';

   var style_green = {
               strokeColor: "#339933",
                strokeOpacity: 1,
                strokeWidth: 3,
                pointRadius: 6,
                pointerEvents: "visiblePainted"
   };
   var style_red = {
               fillColor: "#ff0000",
                strokeOpacity: 1,
                strokeWidth: 3,
                pointRadius: 6,
                pointerEvents: "visiblePainted"
   };
   var style_high = {
                fillColor: "#ff00ff",
                strokeOpacity: 1,
                strokeWidth: 3,
                pointRadius: 6,
                pointerEvents: "visiblePainted"
   };
  slight_layer = new OpenLayers.Layer.Vector("Slight Risk", style_green);
  moderate_layer = new OpenLayers.Layer.Vector("Moderate Risk", style_red);
  high_layer = new OpenLayers.Layer.Vector("High Risk", style_high);

  map.addLayers([wms, slight_layer, moderate_layer, high_layer]);

  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.addControl(new OpenLayers.Control.MousePosition());
            
  function report(event) {
    OpenLayers.Console.log(event.type, event.feature.id);
  }
  slight_layer.events.on({
    "beforefeaturemodified": report,
    "featuremodified": report,
    "afterfeaturemodified": report
  });
            
            


  /* Create Slight Risk */
  pointList = [new OpenLayers.Geometry.Point(-110.0,25.0),
      new OpenLayers.Geometry.Point(-110.0,40.0),
      new OpenLayers.Geometry.Point(-85.0,40.0),
      new OpenLayers.Geometry.Point(-85.0,25.0)];
  pointList.push(pointList[0]);
  slight_layer.addFeatures([
         new OpenLayers.Feature.Vector(
             new OpenLayers.Geometry.Polygon([
               new OpenLayers.Geometry.LinearRing(pointList)
             ])
         )]
  );

  /* Create Moderate Risk */
  pointList = [new OpenLayers.Geometry.Point(-100.0,30.0),
      new OpenLayers.Geometry.Point(-100.0,37.0),
      new OpenLayers.Geometry.Point(-90.0,37.0),
      new OpenLayers.Geometry.Point(-90.0,30.0)];
  pointList.push(pointList[0]);
  moderate_layer.addFeatures([
         new OpenLayers.Feature.Vector(
             new OpenLayers.Geometry.Polygon([
               new OpenLayers.Geometry.LinearRing(pointList)
             ])
         )]
  );


  /* Create High Risk */
  pointList = [new OpenLayers.Geometry.Point(-95.0,33.0),
      new OpenLayers.Geometry.Point(-95.0,36.0),
      new OpenLayers.Geometry.Point(-93.0,36.0),
      new OpenLayers.Geometry.Point(-93.0,33.0)];
  pointList.push(pointList[0]);
  high_layer.addFeatures([
         new OpenLayers.Feature.Vector(
             new OpenLayers.Geometry.Polygon([
               new OpenLayers.Geometry.LinearRing(pointList)
             ])
         )]
  );

  controls = {
    slight_cntrl: new OpenLayers.Control.ModifyFeature_mod(slight_layer),
    mod_cntrl: new OpenLayers.Control.ModifyFeature_mod(moderate_layer),
    high_cntrl: new OpenLayers.Control.ModifyFeature_mod(high_layer)
   };
   map.addControl(controls.slight_cntrl);
   map.addControl(controls.mod_cntrl);
   //controls.mod_cntrl.activate();
   map.addControl(controls.high_cntrl);
   //controls.high_cntrl.activate();
   controls.slight_cntrl.activate();

   

    var mapPanel = new GeoExt.MapPanel({
        title: "GeoExt MapPanel",
        region: "center",
        map: map,
        center: new OpenLayers.LonLat(-95, 42),
        zoom: 4
    });

   var slightCB = new Ext.form.Radio({
       name       : 'editor',
       checked    : true,
       fieldLabel : 'Modify Slight Risk',
       listeners  : {
           check : function(cb, checked){
               if (checked){ 
                   controls.high_cntrl.deactivate();
                   controls.mod_cntrl.deactivate();
                   controls.slight_cntrl.activate(); 
               }
           }
       }
   });
   var modCB = new Ext.form.Radio({
       name       : 'editor',
       fieldLabel : 'Modify Moderate Risk',
       listeners  : {
           check : function(cb, checked){
               if (checked){ 
                   controls.high_cntrl.deactivate();
                   controls.slight_cntrl.deactivate();
                   controls.mod_cntrl.activate(); 
               }
           }
       }
   });
   var highCB = new Ext.form.Radio({
       name       : 'editor',
       fieldLabel : 'Modify High Risk',
       listeners  : {
           check : function(cb, checked){
               if (checked){
                   controls.slight_cntrl.deactivate();
                   controls.mod_cntrl.deactivate(); 
                   controls.high_cntrl.activate();
               }
           }
       }
   });


   var formPanel = new Ext.form.FormPanel({
       region    : 'west',
       height    : 500,
       width     : 200,
       items     : [slightCB, modCB, highCB]
   });

   new Ext.Viewport({
       layout  : 'border',
       items   : [
           {
             contentEl : 'iem-header',
             region    : 'north',
             height    : 140
           }, {
             contentEl : 'iem-footer',
             height    : 60,
             region    : 'south'
           },
           formPanel, mapPanel
       ]
   });

}); /* End of init() */
