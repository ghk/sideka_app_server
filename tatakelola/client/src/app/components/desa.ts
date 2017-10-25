import 'rxjs/add/operator/map';

import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';

import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';

import MapUtils from '../helpers/mapUtils';

interface Data {
    [key: string]: any[]
}

@Component({
    selector: 'desa',
    templateUrl: '../templates/desa.html'
})

export class DesaComponent implements OnInit, OnDestroy {
     activeMenu: string;
     activeMap: L.Map;
     mapOptions: L.MapOptions;
     geoJSONOptions: L.GeoJSONOptions;
     geoJSON: L.GeoJSON;
     data: Data;
     bigConfig: any[];
     pemetaan: any;
     sidebarCollapsed: boolean;
     captions: any;

     constructor(private _http: Http) {}

     ngOnInit(): void {
        this.sidebarCollapsed = false;
        this.captions = { "pembangunan": {"total": 0, "year": 2016 }, 
                        "batas": 0, 
                        "genders": {"female": 0, "male": 0 }, 
                        "education": {"tk": 0, "sd": 0, "smp": 0, "sma": 0, "universitas": 0},
                        "electricity": {"detected": 0, "from": 0},
                        "misc": "none",
                        "networks": "none",
                        "potention": {"farmland": "", "orchard": "", "forest": ""} };
                    
        this.mapOptions = {
            layers: [ L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png') ],
            zoom: 14,
            center: L.latLng([-7.547389769590928, 108.21044272398679])
        }

        this.geoJSONOptions = {
            style: (feature) => {
                return { color: '#000', weight: feature.geometry.type === 'LineString' ? 2 : 1 }
            },
            onEachFeature: (feature, layer) => {
                for(let i=0; i<this.bigConfig.length; i++) {
                    let indicator = this.bigConfig[i];
                    let element = null;

                    for(let j=0; j<indicator.elements.length; j++) {
                        let current = indicator.elements[j];
                        
                         if(current.values) {
                            let valueKeys = Object.keys(current.values);

                            if(valueKeys.every(valueKey => feature["properties"][valueKey] === current.values[valueKey])){
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
            error => {}
        )
       
        this.extractDataFromPemetaan();
     }

     setActiveMenu(menu: string): boolean {
        this.activeMenu = menu;

        switch(this.activeMenu) {
            case 'pembangunan':
               this.setGeoJSONToMap('pembangunan');
                break;
            case 'potensi':
               this.setGeoJSONToMap('potensi');
                break;
            case 'batas':
               this.setGeoJSONToMap('batas');
                break;
        }

        return false;
     }

     ngOnDestroy(): void {}

     setGeoJSONToMap(key: string): void {
        this.clearGeoJSON();

        let selectedData = this.data[key];
        let geoJson = MapUtils.createGeoJson();

        for(let i=0; i<selectedData.length; i++) {
             let spatial = selectedData[i].spatial;
             let feature = MapUtils.createFeature(spatial, selectedData[i].metadata.featureType, selectedData[i].metadata.properties);
             geoJson.features.push(feature);
        }

        this.geoJSON = L.geoJSON(geoJson, this.geoJSONOptions).addTo(this.activeMap);
     }

     clearGeoJSON(): void {
        if(this.geoJSON)
           this.activeMap.removeLayer(this.geoJSON);
     }

     onMapReady(map: L.Map): void {
        this.activeMap = map;
     }

     extractDataFromPemetaan(): void {
        this.data = { pembangunan: [], potensi: [], batas: [] };
        this._http.get('assets/pemetaan.json').map(res => res.json()).subscribe(
            data => {
                this.pemetaan = data;

                let indicatorKeys = Object.keys(this.pemetaan.data);

                for(let i=0; i<indicatorKeys.length; i++) {
                    let key = indicatorKeys[i];

                    if(key === 'log_pembangunan') {
                        //DO SOMETHING
                        continue;
                    }
                    
                    let data = this.pemetaan.data[key];

                    for(let j=0; j<data.length; j++) {
                        let dataItem = data[j];
                        let metadata = { id: dataItem.id, properties: dataItem.properties, featureType: dataItem.geometry.type };
                        let spatial = dataItem.geometry.coordinates;
                        
                        if(dataItem.indicator === 'landuse') 
                            this.data.potensi.push({ spatial: spatial, metadata: metadata });
                        
                        else if(dataItem.indicator === 'boundary') 
                            this.data.batas.push({ spatial: spatial, metadata: metadata });
                    }
                }
                
                console.log(this.data);
            },
            error => {}
        )
     }
}