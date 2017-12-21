import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';
import { Router, ActivatedRoute } from "@angular/router";
import { DataService } from '../services/data';
import { MapUtils } from '../helpers/mapUtils';
import { Progress } from 'angular-progress-http';

import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';

import 'rxjs/add/operator/map';

import BIG from '../helpers/bigConfig';
import geoJSONArea from '@mapbox/geojson-area';

@Component({
    selector: 'st-desa',
    templateUrl: '../templates/desa.html'
})
export class DesaComponent implements OnInit, OnDestroy {
    activeMenu: string;
    map: L.Map;
    options: L.MapOptions;
    sidebarCollapsed: boolean;
    progress: Progress;
    regionId: string;
    summaries: any;
    geoJsonLayout: L.GeoJSON;
    geoJsonSchools: L.GeoJSON;
    geoJsonLanduse: L.GeoJSON;
    geoJsonBoudary: L.GeoJSON;
    geoJsonDesaBoundary: L.GeoJSON;
    geoJsonDusunBoundary: L.GeoJSON;
    availableDesaSummaries: any[];
    currentDesaIndex: number;
    markers: L.Marker[];
    showDesaBoundary: boolean;
    showDusunBoundary: boolean;
    nextDesa: string;
    prevDesa: string;

    constructor(
        private _http: Http,
        private _dataService: DataService,
        private _activeRouter: ActivatedRoute,
        private _router: Router
    ) { }

    ngOnInit(): void {
        this.sidebarCollapsed = false;
        this.markers = [];
        this.showDesaBoundary = true;
        this.showDusunBoundary = true;
        this.prevDesa = 'TIDAK ADA';
        this.nextDesa = 'TIDAK ADA';

        this.progress = {
            percentage: 0,
            event: null,
            lengthComputable: true,
            loaded: 0,
            total: 0,
        }

        this.options = {
            layers: [L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')],
            zoom: 14,
            center: L.latLng([-7.547389769590928, 108.21044272398679])
        }

        this._activeRouter.params.subscribe(
            params => {
                this.regionId = params['regionId'];
                this.setupSummaries(params['regionId']);
                this.setupBoundary(params['regionId']);
                this.getAvailableDesaSummaries(params['regionId']);
            }
         )
    }

    async setupSummaries(regionId: string) {
        this.progress.percentage = 0;

        try{
           
            let summaries = await this._dataService.getSummariesByRegion(regionId, {}, 
                this.progressListener.bind(this)).toPromise();
            
            if(summaries.length > 0)
              this.summaries = summaries[0];

            console.log(this.summaries);
        }
        catch(error) {
            console.log(error);
        }
    }

    async setupBoundary(regionId: string) {
        try {
            this.cleanMarkers();

            let geoJsonLayoutRaw = await this._dataService.getGeojsonByTypeAndRegion('boundary', regionId, {}, 
                this.progressListener.bind(this)).toPromise();
        
            this.setMapLayout(geoJsonLayoutRaw);
            
        }
        catch(error) {
            console.log(error);
        }
    }

    async getAvailableDesaSummaries(regionId: string) {
        this.availableDesaSummaries = await this._dataService.getSummariesExceptId(regionId, null).toPromise();
        this.availableDesaSummaries = this.availableDesaSummaries.concat(this.summaries);
        this.currentDesaIndex = this.availableDesaSummaries.indexOf(this.summaries);
        this.setNextPrevLabel();
    }

    async next() {
        this.activeMenu = null;

        if(this.currentDesaIndex === this.availableDesaSummaries.length - 1)
           return;

        this.cleanLayers();   
        this.cleanLayout();
        this.cleanMarkers();

        this.currentDesaIndex += 1; 
        this.summaries = this.availableDesaSummaries[this.currentDesaIndex];

        this.setNextPrevLabel();
        this.setupBoundary(this.summaries.fk_region_id);
    }
    
    async prev() {
        this.activeMenu = null;
        
        if(this.currentDesaIndex === 0)
          return;

        this.cleanLayers();  
        this.cleanLayout();
        this.cleanMarkers();

        this.currentDesaIndex -= 1;
        this.summaries = this.availableDesaSummaries[this.currentDesaIndex];

        this.setNextPrevLabel();
        this.setupBoundary(this.summaries.fk_region_id);
    }
    
    async setMapSchools() {
        this.cleanLayers(); 
        this.cleanMarkers();

        let regionId = this.summaries.fk_region_id;

        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('facilities_infrastructures', 
                regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = map.data;

        featureCollection.features = featureCollection.features.filter(e => e.properties.amenity 
            && e.properties.amenity === 'school' && e.properties.isced);
       
        this.geoJsonSchools = L.geoJSON(featureCollection);
        this.geoJsonSchools.addTo(this.map);
    }
    
    async setMapLanduse() {
        this.cleanLayers(); 
        this.cleanMarkers();

        let regionId = this.summaries.fk_region_id;
        
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('landuse', 
                regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = map.data;

        featureCollection.features = featureCollection.features.filter(e => e.properties.landuse);

        this.geoJsonLanduse = L.geoJSON(featureCollection, {
            onEachFeature: this.onEachFeature.bind(this)
        });

        this.geoJsonLanduse.addTo(this.map);

        for (let i=0; i<featureCollection.features.length; i++) {
            let feature = featureCollection.features[i];
            let center = L.geoJSON(feature).getBounds().getCenter();
            let marker = null;
            let url = null;

            /*
            if (feature.properties.landuse && feature.properties.landuse === 'farmland') {
                if (feature.properties.crop && feature.properties.crop === 'padi')
                    url = '/assets/images/pertanian.png';
                else if (feature.properties.crop && feature.properties.crop === 'jagung')
                    url = '/assets/images/corn.png';
            }
            else if (feature.properties.landuse && feature.properties.landuse === 'orchard') {
                if (feature.properties.crop && feature.properties.crop === 'bawang')
                    url = '/assets/images/garlic.png';
            }*/

            if (feature.properties.landuse && feature.properties.landuse === 'farmland') 
                url =  '/assets/images/pertanian.png';

            else if (feature.properties.landuse && feature.properties.landuse === 'orchard') 
                url =  '/assets/images/perkebunan.png';

            else if (feature.properties.landuse && feature.properties.landuse === 'forest')
                url =  '/assets/images/hutan.png';
            
            if (!url)
                continue;

            marker = L.marker(center, {
                icon: L.icon({ 
                    iconUrl: url,
                    iconSize: [20, 20],
                    shadowSize: [50, 64],
                    iconAnchor: [22, 24],
                    shadowAnchor: [4, 62],
                    popupAnchor: [-3, -76]
                })
            }).addTo(this.map);

            this.markers.push(marker);
        }
    }

    async setMapLogPembangunan() {
        this.cleanLayers(); 
        
        this.progress.percentage = 0;

        let regionId = this.summaries.fk_region_id;

        let landuse = await this._dataService.getGeojsonByTypeAndRegion('landuse', 
            regionId, {}, this.progressListener.bind(this)).toPromise();

        let infrastructures = await this._dataService.getGeojsonByTypeAndRegion('facilities_infrastructures', 
            regionId, {}, this.progressListener.bind(this)).toPromise();

        let logPembangunan = await this._dataService.getGeojsonByTypeAndRegion('log_pembangunan', 
            regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = landuse.data;

        featureCollection.features  = featureCollection.features.filter(e => e.properties.landuse);
        featureCollection.features = featureCollection.features.concat(infrastructures.data.features);

        this.geoJsonLanduse = L.geoJSON(featureCollection, {
            onEachFeature: this.onEachFeature.bind(this)
        });

        console.log(logPembangunan);
    }

    async setMapBoundary() {
        this.cleanLayers(); 
        this.setDusunBoundary();
        this.setDesaBoundary();
    }

    async setDusunBoundary() {
        let regionId = this.summaries.fk_region_id;
        
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('boundary', 
        regionId, {}, this.progressListener.bind(this)).toPromise();

        let features = map.data.features.filter(e => e.properties.admin_level && e.properties.admin_level == 8);

        this.markers = [];

        for (let i=0; i<features.length; i++) {
            let area = geoJSONArea.geometry(features[i].geometry);
            
            let marker = L.marker(L.geoJSON(features[i]).getBounds().getCenter(), {
                icon: L.divIcon({
                    className: 'label', 
                    html: '<h4 style="color: blue;"><strong>' + Math.round(area / 10000) + ' Ha </strong></h4>',
                    iconSize: [30, 30]
                  })
            }).addTo(this.map);

            this.markers.push(marker);
        }

        this.geoJsonDusunBoundary = L.geoJSON(features, {
            style: (feature) => {
                return { fillColor: '#000', color: '#fff', weight: 1 };
            },
            onEachFeature: (feature, layer) => {

            }
        }).addTo(this.map);
    }

    async setDesaBoundary() {
        let regionId = this.summaries.fk_region_id;
        
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('boundary', 
        regionId, {}, this.progressListener.bind(this)).toPromise();

        let features = map.data.features.filter(e => e.properties.admin_level && e.properties.admin_level == 7); 

        this.geoJsonDesaBoundary = L.geoJSON(features, {
            style: (feature) => {
                return { color: '#000', weight: 1 };
            },
            onEachFeature: (feature, layer) => {
                if (feature.properties['boundary_sign']) {
                    layer['setStyle'](MapUtils.setupStyle({ dashArray: feature.properties['boundary_sign']}));
                }
            }
        }).addTo(this.map);
    }

    setMapLayout(geoJsonLayoutRaw: any): void {
        this.geoJsonLayout = L.geoJSON(geoJsonLayoutRaw.data, {
            style: this.getMapBoundaryStyle.bind(this),
            onEachFeature: this.onEachFeature.bind(this)
        });

        this.geoJsonLayout.addTo(this.map);
        this.map.flyTo(this.geoJsonLayout.getBounds().getCenter(), 15);
    }

    setActiveMenu(menu: string) {
        this.activeMenu = menu;

        switch(menu) {
            case 'schools':
                this.setMapSchools();
            break;
            case 'landuse':
                this.setMapLanduse();
            break;
            case 'apbdes':
                this.setMapLogPembangunan();
            break;
            case 'boundary':
                this.setMapBoundary();
            break;
        }
        return false;
    }

    getMapBoundaryStyle(feature) {
        return { color: '#aaa', weight: 0.5 };
    }

    onEachFeature(feature, layer) {
        for (let index in BIG) {
            let indicator = BIG[index];
            let elements = indicator.elements;
            let matchedElement = null;

            for (let index in elements) {
                let indicatorElement = elements[index];

                if (!indicatorElement.values)
                   continue;
                
                let valueKeys = Object.keys(indicatorElement.values);

                if (valueKeys.every(valueKey => feature["properties"][valueKey] 
                    === indicatorElement.values[valueKey])) {
                    matchedElement = indicatorElement;
                    break;
                }
            }

            if (!matchedElement)
                continue;

            if (matchedElement['style']) {
                let style = MapUtils.setupStyle(matchedElement['style']);
                layer['setStyle'] ? layer['setStyle'](style) : null;
            }

            if (feature.properties['boundary_sign']) { 
                let style = MapUtils.setupStyle({ dashArray: feature.properties['boundary_sign'] });
                layer.setStyle(style);
            }
        }
    }

    onMapReady(map: L.Map): void {
        this.map = map;
    }

    
    setNextPrevLabel() {
        this.nextDesa = this.availableDesaSummaries[this.currentDesaIndex + 1] 
            ? this.availableDesaSummaries[this.currentDesaIndex + 1].region.name : 'TIDAK ADA';
    
        this.prevDesa = this.availableDesaSummaries[this.currentDesaIndex - 1] 
            ? this.availableDesaSummaries[this.currentDesaIndex - 1].region.name : 'TIDAK ADA';
    }

    cleanLayers(): void {
        if (this.geoJsonSchools)
            this.map.removeLayer(this.geoJsonSchools);
        if (this.geoJsonLanduse)
            this.map.removeLayer(this.geoJsonLanduse);
        if (this.geoJsonDusunBoundary)
            this.map.removeLayer(this.geoJsonDusunBoundary);
        if (this.geoJsonDesaBoundary)
            this.map.removeLayer(this.geoJsonDesaBoundary);
    }

    cleanLayout(): void {
        if (this.geoJsonLayout)
            this.map.removeLayer(this.geoJsonLayout);
    }

    cleanMarkers(): void {
        for (let i=0; i<this.markers.length; i++)
            this.map.removeLayer(this.markers[i]);

        this.markers = [];
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

    ngOnDestroy(): void {}
}