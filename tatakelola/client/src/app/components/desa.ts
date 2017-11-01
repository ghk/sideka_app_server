import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';
import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';

import { DataService } from '../services/data';
import { MapUtils } from '../helpers/mapUtils';

@Component({
    selector: 'st-desa',
    templateUrl: '../templates/desa.html'
})
export class DesaComponent implements OnInit, OnDestroy {
    activeMenu: string;
    activeMap: L.Map;
    mapOptions: L.MapOptions;
    geoJSONOptions: L.GeoJSONOptions;
    geoJSON: L.GeoJSON;
    data: any[];
    bigConfig: any[];
    pemetaan: any;
    sidebarCollapsed: boolean;
    captions: any;

    constructor(
        private _http: Http,
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        this.sidebarCollapsed = false;
        this.captions = {
            "pembangunan": { "total": 0, "year": 2016 },
            "batas": 0,
            "genders": { "female": 0, "male": 0 },
            "education": { "tk": 0, "sd": 0, "smp": 0, "sma": 0, "universitas": 0 },
            "electricity": { "detected": 0, "from": 0 },
            "misc": "none",
            "networks": "none",
            "potention": { "farmland": "", "orchard": "", "forest": "" }
        };

        this.mapOptions = {
            layers: [L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')],
            zoom: 14,
            center: L.latLng([-7.547389769590928, 108.21044272398679])
        }

        this.geoJSONOptions = {
            style: (feature) => {
                return { color: '#000', weight: feature.geometry.type === 'LineString' ? 2 : 1 }
            },
            onEachFeature: (feature, layer) => {
                for (let i = 0; i < this.bigConfig.length; i++) {
                    let indicator = this.bigConfig[i];
                    let element = null;

                    for (let j = 0; j < indicator.elements.length; j++) {
                        let current = indicator.elements[j];

                        if (current.values) {
                            let valueKeys = Object.keys(current.values);

                            if (valueKeys.every(valueKey => feature["properties"][valueKey] === current.values[valueKey])) {
                                element = current;
                                break;
                            }
                        }
                    }

                    if (!element)
                        continue;

                    if (element['style']) {
                        let style = MapUtils.setupStyle(element['style']);
                        layer['setStyle'](style);
                    }
                }
            }
        }

        this._http.get('assets/bigConfig.json').map(res => res.json()).subscribe(
            data => {
                this.bigConfig = data;
            },
            error => { }
        )

        this._dataService.getGeojsonsByRegion('32.06.19.2010', null, null).subscribe(
            data => {
                this.data = data;
                this.addGeoJSONToMap('facilities_infrastructures');
            },
            error => { }
        )
    }

    ngOnDestroy(): void { }

    setActiveMenu(menu: string): boolean {
        this.activeMenu = menu;

        switch (this.activeMenu) {
            case 'pembangunan':
                this.addGeoJSONToMap('facilities_infrastructures');
                break;
            case 'potensi':
                this.addGeoJSONToMap('landuse');
                break;
            case 'batas':
                this.addGeoJSONToMap('boundary');
                break;
        }

        return false;
    }

    addGeoJSONToMap(key: string): void {
        this.clearGeoJSON();

        let selectedData = null;

        this.data.forEach(datum => {
            if (datum.type === key)
                selectedData = datum;
        });

        if (selectedData) {
            console.log(selectedData);
            this.geoJSON = L.geoJSON(JSON.parse(selectedData.data), this.geoJSONOptions).addTo(this.activeMap);
        }
    }

    clearGeoJSON(): void {
        if (this.geoJSON)
            this.activeMap.removeLayer(this.geoJSON);
    }

    onMapReady(map: L.Map): void {
        this.activeMap = map;
    }

}