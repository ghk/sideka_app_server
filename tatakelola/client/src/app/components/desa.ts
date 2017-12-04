import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';
import { Router, ActivatedRoute } from "@angular/router";
import { DataService } from '../services/data';
import { MapUtils } from '../helpers/mapUtils';
import { Progress } from 'angular-progress-http';

import BIG from '../helpers/bigConfig';
import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';

import 'rxjs/add/operator/map';

@Component({
    selector: 'st-desa',
    templateUrl: '../templates/desa.html'
})
export class DesaComponent implements OnInit, OnDestroy {
    activeMenu: string;
    activeMap: L.Map;
    mapOptions: L.MapOptions;
    geoJSONOptions: L.GeoJSONOptions;
    data: any[];
    sidebarCollapsed: boolean;
    summaries: any;
    progress: Progress;
    farmlands: string;
    orchards: string;
    trees: string;
    geoJsonLayer: L.GeoJSON;
    availableDesas: any[];
    currentIndex: number;
    activeRegionId: string;
    activeDesa: string;

    constructor(
        private _http: Http,
        private _dataService: DataService,
        private _activeRouter: ActivatedRoute,
        private _router: Router
    ) { }

    ngOnInit(): void {
        this.sidebarCollapsed = false;
        this.summaries = {};
        this.availableDesas = [];
        this.progress = {
            percentage: 0,
            event: null,
            lengthComputable: true,
            loaded: 0,
            total: 0,
        }

        this.mapOptions = {
            layers: [L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')],
            zoom: 14,
            center: L.latLng([-7.547389769590928, 108.21044272398679])
        }
        
        this._activeRouter.params.subscribe(
           params => {
               let regionId = params['regionId'];
               this.activeRegionId = regionId;
               this.setup();
           }
        )

        this.geoJSONOptions = {
            style: (feature) => {
                return { color: '#000', weight: 0.5 }
            },
            onEachFeature: (feature, layer) => {
                 for (let i = 0; i < BIG.length; i++) {
                    let indicator = BIG[i];
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
    }

    setup(): void {
        this.activeDesa = null;
        this.loadGeojsonByRegion();
        this.loadSummariesByRegion();

        if(this.availableDesas.length === 0)
            this.loadAvailableMaps();
    }

    private loadGeojsonByRegion(): void {
        this.clearMap();
        this.progress.percentage = 0;

        this._dataService.getGeojsonsByRegion(this.activeRegionId, {}, this.progressListener.bind(this)).subscribe(
            geojson => {
                if(geojson.length === 0)
                    return;

                this.setMapLayout(geojson);
            }
        )
    }

    private loadSummariesByRegion(): void {
        this._dataService.getSummariesByRegion(this.activeRegionId, {}, null).subscribe(
            summaries => {
                if(summaries.length > 0) {
                    this.summaries = summaries[0];
                    this.activeDesa = this.summaries.region.name;
                }
            }
        )
    }

    private loadAvailableMaps(): void {
        this._dataService.getRegionAvailableMaps({}, null).subscribe(
            summaries => {
                this.availableDesas = summaries;
                
                let thisRegion = this.availableDesas.filter(e => e.region.id === this.activeRegionId)[0];
                this.currentIndex = this.availableDesas.indexOf(thisRegion);
            }
        )
    }

    next(): void {
        this.currentIndex += 1;

        if(this.availableDesas.length - 1 < this.currentIndex)
            return;
        
        this.activeRegionId = this.availableDesas[this.currentIndex].region.id;
        this.setup();
    }

    prev(): void {
        if(this.currentIndex === 0)
            return;
       
        this.currentIndex -= 1;
    
        this.activeRegionId = this.availableDesas[this.currentIndex].region.id;
        this.setup();
    }

    ngOnDestroy(): void { }

    setActiveMenu(menu: string): boolean {
        this.activeMenu = menu;
        switch(menu){
            case 'pembangunan':
            break;
            case 'batas':
            break;
        }
        return false;
    }

    setMapLayout(geoJson): void {
        let landuse = geoJson.filter(e => e.type === 'landuse')[0];
        let transport = geoJson.filter(e => e.type === 'network_transportation')[0];
        let facilities = geoJson.filter(e => e.type === 'facilities_infrastructures')[0];
        let waters = geoJson.filter(e => e.type === 'waters')[0];
        let boundary = geoJson.filter(e => e.type === 'boundary')[0];
       
        let geoJsonData: any = MapUtils.createGeoJson();

        if(waters)
            geoJsonData.features = geoJsonData.features.concat(waters.data.features);
        if(transport)
            geoJsonData.features = geoJsonData.features.concat(transport.data.features); 
        if(landuse)
            geoJsonData.features = geoJsonData.features.concat(landuse.data.features);
    
        this.geoJsonLayer = L.geoJSON(geoJsonData, this.geoJSONOptions).addTo(this.activeMap);

        this.activeMap.setView(this.geoJsonLayer.getBounds().getCenter(), 15);
    }

    clearMap(): void {
        if (this.geoJsonLayer)
            this.activeMap.removeLayer(this.geoJsonLayer);
    }

    onMapReady(map: L.Map): void {
        this.activeMap = map;
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
}