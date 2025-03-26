/* global $, Ext, app, cfg */
Ext.namespace('app');
Ext.namespace('cfg');
cfg.refreshint = 60000;
cfg.header = 'iem-header';
cfg.headerHeight = 60;
cfg.jsonSource = '/json/webcams.json';
let imagestore = null;
let disableStore = null;
const ISO8601 = 'Y-m-d\\TH:i:s\\Z';

/**
 * Convert a date to UTC
 * @param {Date} dt 
 * @returns 
 */
function toUTC(dt) {
    return Ext.Date.add(dt, Ext.Date.MINUTE, dt.getTimezoneOffset());
}

/**
 * Convert a date from UTC
 * @param {Date} dt
 * @returns
 */
function fromUTC(dt) {
    return Ext.Date.add(dt, Ext.Date.MINUTE, -dt.getTimezoneOffset());
}

Ext.onReady(() => {

    $(".ccool").click((event) => {
        const target = $(event.target);
        app.appSetTime(target.data("opt"));
    });

    /* Hack needed for Ext 3.0-rc2 to keep timefield working */
    Ext.override(Ext.form.ComboBox, {
        beforeBlur: Ext.emptyFn
    });

    // Set up a model to use in our Store
    Ext.define('Image', {
        extend: 'Ext.data.Model',
        fields: [
            { name: 'cid', type: 'string' },
            { name: 'show', type: 'boolean', defaultValue: true },
            { name: 'name', type: 'string' },
            { name: 'county', type: 'string' },
            { name: 'network', type: 'string' },
            { name: 'url', type: 'string' }
        ]
    });

    disableStore = new Ext.data.Store({
        idProperty: 'cid',
        model: 'Image'
    });

    imagestore = new Ext.data.JsonStore({
        isLoaded: false,
        proxy: {
            type: 'ajax',
            url: cfg.jsonSource,
            reader: {
                type: 'json',
                idProperty: 'cid',
                rootProperty: 'images'
            }
        },
        model: 'Image'
    });
    /*
     * When the image store loads, we need to check our listing of disabled
     * webcams so that we don't show it again
     */
    imagestore.on('load', (_store, records) => {
        const data = Array();
        Ext.each(records, (record) => {
            const checked = (disableStore.find('cid', record.get("cid")) === -1);
            data.push({
                boxLabel: Number(record.get("cid").substr(5, 3)) + " " + record.get("name"),
                name: record.get("cid"),
                checked,
                listeners: {
                    change(cb, isChecked) {
                        const id = cb.getName();
                        if (!imagestore.isLoaded) { return; }

                        let rec = imagestore.getAt(imagestore.find("cid", id));
                        rec.set('show', isChecked, { silent: true });
                        if (isChecked) {
                            rec = disableStore.getAt(disableStore.find('cid', id));
                            disableStore.remove(rec);
                            imagestore.sort(Ext.getCmp("sortSelect").getValue(), "ASC");
                        } else {
                            disableStore.add(rec);
                            imagestore.sort(Ext.getCmp("sortSelect").getValue(), "ASC");
                        }
                    }
                }
            });
        });
        if (Ext.getCmp("camselector")) {
            Ext.getCmp("camselector").destroy();
        }
        if (records.length > 0) {
            Ext.getCmp("cameralist").add({
                xtype: 'checkboxgroup',
                columns: 1,
                id: 'camselector',
                hideLabel: true,
                items: data
            });
            Ext.getCmp("cameralist").doLayout();
        } else {
            Ext.Msg.alert('Status', 'Sorry, no images found for this time. '
                + 'Try selecting a time divisible by 5.');
        }
        imagestore.isLoaded = true;
    });


    const tpl = new Ext.XTemplate(
        '<tpl for=".">',
        '<tpl if="this.shouldShow(cid)">',
        '<div class="thumb-wrap" id="{cid}">',
        '<div class="thumb"><img class="webimage" src="{url}" title="{name}"></div>',
        '<span>[{cid}] {name}, {state} ({county} County)</span></div>',
        '</tpl>',
        '</tpl>',
        '<div class="x-clear"></div>',
        {
            shouldShow(cid) {
                return (disableStore.find('cid', cid) === -1);
            }
        }
    );

    const helpWin = new Ext.Window({
        contentEl: 'help',
        title: 'Information',
        closeAction: 'hide',
        width: 400
    });

    Ext.create('Ext.Panel', {
        renderTo: 'main',
        height: Ext.getBody().getViewSize().height - 120,
        layout: {
            type: 'border',
            align: 'stretch'
        },
        items: [{
            xtype: 'form',
            id: 'cameralist',
            region: 'west',
            collapsible: true,
            autoScroll: true,
            title: "Select Webcams",
            tbar: [{
                xtype: 'button',
                text: 'All Off',
                handler() {
                    Ext.getCmp("camselector").items.each((i) => {
                        i.setValue(false);
                    });
                }
            }, {
                xtype: 'button',
                text: 'All On',
                handler()  {
                    Ext.getCmp("camselector").items.each((i) => {
                        i.setValue(true);
                    });
                }
            }]
        }, {
            region: 'center',
            xtype: 'panel',
            autoScroll: true,
            items: [{
                xtype: 'dataview',
                store: imagestore,
                itemSelector: 'div.thumb-wrap',
                autoHeight: true,
                overItemCls: 'x-view-over',
                emptyText: "No Images Loaded or Selected for Display",
                tpl
            }],
            tbar: [{
                xtype: 'button',
                text: 'Help',
                handler() {
                    helpWin.show();
                }
            }, {
                xtype: 'tbtext',
                text: 'Sort By:'
            }, {
                xtype: 'combo',
                id: 'sortSelect',
                triggerAction: 'all',
                width: 80,
                editable: false,
                mode: 'local',
                displayField: 'desc',
                valueField: 'name',
                lazyInit: false,
                value: 'name',
                store: new Ext.data.ArrayStore({
                    fields: ['name', 'desc'],
                    data: [['name', 'Name'], ['county', 'County'], ['cid', 'Camera ID']]
                }),
                listeners: {
                    'select': (sb) => {
                        imagestore.sort(sb.getValue(), "ASC");
                    }
                }
            }, {
                xtype: 'combo',
                id: 'networkSelect',
                triggerAction: 'all',
                width: 140,
                editable: false,
                mode: 'local',
                displayField: 'desc',
                valueField: 'name',
                lazyInit: false,
                value: 'name',
                store: new Ext.data.ArrayStore({
                    fields: ['name', 'desc'],
                    data: [['IDOT', 'Iowa DOT RWIS'],
                    ['KCCI', 'KCCI-TV Des Moines'],
                    ['KCRG', 'KCRG-TV Cedar Rapids'],
                    ['KELO', 'KELO-TV Sioux Falls'],
                    ['MCFC', 'McLaughlin Family of Companies']]
                }),
                listeners: {
                    'select': () => {
                        imagestore.isLoaded = false;
                        let ts = Ext.Date.format(Ext.getCmp("datepicker").getValue(), 'm/d/Y')
                            + " " + Ext.getCmp("timepicker").getRawValue();
                        const dt = new Date(ts);
                        if (Ext.getCmp("timemode").realtime) { ts = 0; }
                        else { ts = Ext.Date.format(toUTC(dt), ISO8601); }
                        imagestore.reload({
                            add: false,
                            params: {
                                ts,
                                'network': Ext.getCmp("networkSelect").getValue()
                            }
                        });
                        window.location.href = `#${Ext.getCmp("networkSelect").getValue()}-${ts}`;
                    }
                }

            }, {
                xtype: 'tbseparator'
            }, {
                xtype: 'button',
                id: 'timemode',
                text: 'Real Time Mode',
                realtime: true,
                handler(btn) {
                    if (btn.realtime) {
                        Ext.getCmp("datepicker").enable();
                        Ext.getCmp("timepicker").enable();
                        btn.setText("Archived Mode");
                        btn.realtime = false;
                    } else {
                        Ext.getCmp("datepicker").disable();
                        Ext.getCmp("timepicker").disable();
                        btn.setText("Real Time Mode");
                        btn.realtime = true;
                        imagestore.isLoaded = false;
                        imagestore.reload({
                            add: false, params: {
                                'network': Ext.getCmp("networkSelect").getValue()
                            }
                        });
                        window.location.href = `#${Ext.getCmp("networkSelect").getValue()}-0`;
                    }
                }
            }, {
                xtype: 'datefield',
                id: 'datepicker',
                maxValue: new Date(),
                emptyText: 'Select Date',
                minValue: '07/23/2003',
                value: new Date(),
                width: 100,
                disabled: true,
                listeners: {
                    select() {
                        imagestore.isLoaded = false;
                        const ts = Ext.Date.format(Ext.getCmp("datepicker").getValue(), 'm/d/Y')
                            + " " + Ext.getCmp("timepicker").getRawValue();
                        const dt = new Date(ts);
                        imagestore.reload({
                            add: false,
                            params: {
                                'ts': Ext.Date.format(toUTC(dt), ISO8601),
                                'network': Ext.getCmp("networkSelect").getValue()
                            }
                        });
                        window.location.href = `#${Ext.getCmp("networkSelect").getValue()}-${Ext.Date.format(toUTC(dt), 'YmdHi')}`;
                    }
                }
            }, {
                xtype: 'timefield',
                allowBlank: false,
                increment: 1,
                width: 100,
                emptyText: 'Select Time',
                id: 'timepicker',
                value: new Date(),
                disabled: true,
                listeners: {
                    select: () => {
                        imagestore.isLoaded = false;
                        const ts = Ext.Date.format(Ext.getCmp("datepicker").getValue(),
                            'm/d/Y')
                            + " " + Ext.getCmp("timepicker").getRawValue();
                        const dt = new Date(ts);
                        imagestore.reload({
                            add: false,
                            params: {
                                'ts': Ext.Date.format(toUTC(dt), ISO8601),
                                'network': Ext.getCmp("networkSelect").getValue()
                            }
                        });
                        window.location.href = "#" + Ext.getCmp("networkSelect").getValue() + "-" + Ext.Date.format(toUTC(dt), 'YmdHi');
                    }
                }
            }
            ]
        }]
    });


    const task = {
        run() {
            if (imagestore.data.length > 0 && Ext.getCmp("timemode") &&
                Ext.getCmp("timemode").realtime) {
                imagestore.reload({
                    add: false,
                    params: {
                        'network': Ext.getCmp("networkSelect").getValue()
                    }
                });
            }
        },
        interval: cfg.refreshint
    };
    Ext.TaskManager.start(task);

    app.appSetTime = (s) => {
        if (s.length === 17) {
            const tokens2 = s.split("-");
            const network = tokens2[0];
            Ext.getCmp("networkSelect").setValue(network);
            const tstamp = tokens2[1];
            const dt = Ext.Date.parseDate(tstamp, 'YmdHi');
            Ext.getCmp("datepicker").setValue(fromUTC(dt));
            Ext.getCmp("timepicker").setValue(fromUTC(dt));
            Ext.getCmp("datepicker").enable();
            Ext.getCmp("timepicker").enable();
            Ext.getCmp("timemode").setText("Archived Mode");
            Ext.getCmp("timemode").realtime = false;
            imagestore.isLoaded = false;
            imagestore.reload({
                add: false,
                params: {
                    'ts': Ext.Date.format(dt, ISO8601),
                    'network': Ext.getCmp("networkSelect").getValue()
                }
            });
            window.location.href = "#" + Ext.getCmp("networkSelect").getValue() + "-" + Ext.Date.format(dt, 'YmdHi');
        } else if (s.length === 6) {
            const tokens3 = s.split("-");
            Ext.getCmp("networkSelect").setValue(tokens3[0]);
            imagestore.load({
                add: false, params: { 'network': tokens3[0] }
            });
        } else {
            imagestore.load();
            Ext.getCmp("networkSelect").setValue("KCCI");
        }
    };

    // Anchor bookmark support
    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        app.appSetTime(tokens[1]);
    } else {
        imagestore.load();
        Ext.getCmp("networkSelect").setValue("KCCI");
    }

});
