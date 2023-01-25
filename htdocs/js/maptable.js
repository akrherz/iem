/* A combination Openlayers Map + DataTable

Example:

<div
    class="iem-maptable row"
    data-label-field="sname"
    data-geojson-src="/geojson/networks.geojson?network=IA_ASOS">
</div>

*/
// https://datatables.net/plug-ins/api/row().show()
$.fn.dataTable.Api.register('row().show()', function () { // needs this
    const page_info = this.table().page.info();
    // Get row index
    const new_row_index = this.index();
    // Row position
    const row_position = this.table()
        .rows({ search: 'applied' })[0]
        .indexOf(new_row_index);
    // Already on right page ?
    if ((row_position >= page_info.start && row_position < page_info.end) || row_position < 0) {
        // Return row object
        return this;
    }
    // Find page number
    const page_to_display = Math.floor(row_position / this.table().page.len());
    // Go to that page
    this.table().page(page_to_display);
    // Return row object
    return this;
});

function get_style(color, text) {
    return new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.6)'
        }),
        text: new ol.style.Text({
            font: '14px Calibri,sans-serif',
            text,
            fill: new ol.style.Fill({
                color: color,
                width: 1
            }),
            stroke: new ol.style.Stroke({
                color: '#FFF',
                width: 3
            })
        })
    });
}

function getLabelForFeature(inst, feat) {
    let label = "TBD";
    if (inst.label_field == "id") {
        label = feat.getId();
    } else if (inst.label_field) {
        label = feat.get(inst.label_field).toString();
    }
    return label;
}

function highlightFeature(inst, feat) {
    if (inst.selectedFeature) {
        inst.selectedFeature.setStyle(null);
    }
    inst.selectedFeature = feat;
    feat.setStyle(get_style("#F00", getLabelForFeature(inst, feat)));
}

function init_map(idx, inst) {
    inst.selectedFeature = null;
    inst.vectorLayer = new ol.layer.Vector({
        title: 'Data',
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => {
            return [get_style("#000", getLabelForFeature(inst, feature))];
        }
    });
    $.ajax({
        method: "GET",
        url: inst.geojson_src,
        dataType: "json",
        success: (data) => {
            if (data.meta) {
                inst.label_field = data.meta.propdefault;
                inst.proporder = data.meta.proporder;
            }
            inst.vectorLayer.getSource().addFeatures(
                (new ol.format.GeoJSON({ featureProjection: 'EPSG:3857' })).readFeatures(data)
            );
        }
    });
    inst.map = new ol.Map({
        target: inst.mapdiv,
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            inst.vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });
    inst.map.on('click', (evt) => {
        const feature = inst.map.forEachFeatureAtPixel(evt.pixel,
            (feature2, _layer) => {
                return feature2;
            });
        if (!feature) {
            return;
        }
        highlightFeature(inst, feature);
        const id = feature.getId();
        inst.table.rows().deselect();
        inst.table.row(
            inst.table.rows((idx2, data, _node) => {
                if (data["id"] === id) {
                    inst.table.row(idx2).select();
                    return true;
                }
                return false;
            })
        ).show().draw(false);

    });

    inst.vectorLayer.getSource().on('change', (_e2) => {
        if (inst.vectorLayer.getSource().getState() == 'ready' && inst.zoomReset === false) {
            inst.map.getView().fit(
                inst.vectorLayer.getSource().getExtent(),
                {
                    size: inst.map.getSize(),
                    padding: [50, 50, 50, 50]
                }
            );
            inst.zoomReset = true;
        }
        if (inst.table) {
            return;
        }
        const columns = [{ title: 'ID', data: 'id' }];
        $(inst.select).append(
            '<option value="id">ID</option>'
        );
        const data = [];
        // If we have a column order, use it!
        if (inst.proporder) {
            inst.proporder.forEach((val) => {
                columns.push({ title: val, data: val })
                $(inst.select).append(
                    `<option value="${val}">${val}</option>`
                );
            });
        }
        inst.vectorLayer.getSource().getFeatures().forEach((feat) => {
            if (columns.length == 1) {
                feat.getKeys().forEach(function (key) {
                    if (key == "geometry") {
                        return;
                    }
                    $(inst.select).append(
                        `<option value="${key}">${key}</option>`
                    );
                    columns.push({ title: key, data: key });
                });
            }
            if (!inst.label_field) {
                inst.label_field = "id";
            }
            $(inst.select).val(inst.label_field);
            const props = feat.getProperties();
            props.id = feat.getId();
            data.push(props);
        });
        inst.table = $(`#maptable-table${idx}`).DataTable({
            columns,
            data,
            select: true
        });
        inst.table.on('select', (_e, dt, type, indexes) => {
            if (type !== 'row') {
                return;
            }
            const featid = dt.row(indexes).data().id;
            const feat = inst.vectorLayer.getSource().getFeatureById(featid);
            highlightFeature(inst, feat);
        });
    });

}

function init(idx, div) {
    // Setup the given div for usage
    // Add left and right hand side divs
    const inst = {};
    inst.proporder = null;
    inst.zoomReset = false;
    inst.geojson_src = $(div).data('geojson-src');
    inst.label_field = $(div).data('label-field');
    const leftcol = document.createElement('div');
    leftcol.className = 'col-md-6';
    inst.mapdiv = document.createElement('div');
    inst.mapdiv.style = "height: 400px";
    leftcol.append(inst.mapdiv);
    const pp = document.createElement('p');
    const tt = document.createTextNode("Select variable for labels:");
    pp.appendChild(tt);
    inst.select = document.createElement('select');
    pp.appendChild(inst.select);
    $(inst.select).on("change", function () { // this
        inst.label_field = this.value;
        inst.vectorLayer.setStyle(inst.vectorLayer.getStyle());
        if (inst.selectedFeature) {
            highlightFeature(inst, inst.selectedFeature);
        }
    });
    leftcol.appendChild(pp);
    div.append(leftcol);
    const tablediv = document.createElement('div');
    tablediv.className = 'col-md-6';
    const tableElement = document.createElement('table');
    tableElement.id = `maptable-table${idx}`;
    tablediv.appendChild(tableElement);
    div.append(tablediv);

    init_map(idx, inst);
    return inst;
}

// https://learn.jquery.com/plugins/basic-plugin-creation/
(function ($) {

    $.fn.MapTable = function (_options) { // this
        const res = [];
        this.each(function (idx, item) {
            res.push(init(idx, item));
        });
        return res;
    };

}(jQuery));