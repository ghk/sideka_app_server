import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';
import { Router, ActivatedRoute } from "@angular/router";
import { DataService } from '../services/data';
import { MapUtils } from '../helpers/mapUtils';
import { Progress } from 'angular-progress-http';
import { ChartHelper } from '../helpers/chartHelper';

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
    geoJsonHighway: L.GeoJSON;
    availableDesaSummaries: any[];
    currentDesaIndex: number;
    markers: L.Marker[];
    showDesaBoundary: boolean;
    showDusunBoundary: boolean;
    nextDesa: string;
    prevDesa: string;
    isLegendShown: boolean;
    isPekerjaanStatisticShown: boolean;
    isPendidikanStatisticShown: boolean;
    isPekerjaanContextShown: boolean;
    isPendidikanContextShown: boolean;
    legends: any[];
    chartHelper: ChartHelper;
    penduduks: any[];
    isToggleContext: boolean;

    constructor(
        private _http: Http,
        private _dataService: DataService,
        private _activeRouter: ActivatedRoute,
        private _router: Router
    ) { }

    ngOnInit(): void {
        this.sidebarCollapsed = false;
        this.showDesaBoundary = true;
        this.showDusunBoundary = true;
        this.isLegendShown = false;
        this.isPekerjaanStatisticShown = false;
        this.isPendidikanStatisticShown = false;
        this.isPekerjaanContextShown = true;
        this.isPendidikanContextShown = true;
        this.isToggleContext = true;

        this.prevDesa = '-';
        this.nextDesa = '-';

        this.markers = [];
        this.legends = [];

        this.chartHelper = new ChartHelper();

        this.progress = {
            percentage: 0,
            event: null,
            lengthComputable: true,
            loaded: 0,
            total: 0,
        }

        this.options = {
            layers: [L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'), ],
            zoom: 5,
            center: L.latLng([-2.604236, 116.499023])
        }

        this._activeRouter.params.subscribe(
            params => {
                this.regionId = params['regionId'];
                this.setupSummaries(params['regionId']);
                this.setupLayout(params['regionId']);
                this.setupPenduduks(params['regionId']);
                this.getAvailableDesaSummaries(params['regionId']);
            }
         )
    }

    toggleShowPendudikan() {
        if (this.isToggleContext)
            this.isPendidikanContextShown = !this.isPendidikanContextShown;
    }

    async setupSummaries(regionId: string) {
        this.progress.percentage = 0;

        try{
           
            let summaries = await this._dataService.getSummariesByRegion(regionId, {}, 
                this.progressListener.bind(this)).toPromise();
            
            if(summaries.length > 0)
              this.summaries = summaries[0];
        }
        catch(error) {
            console.log(error);
        }
    }

    async setupPenduduks(regionId) {
        this.penduduks = await this._dataService.getPenduduksByRegion(regionId, {}, null).toPromise();
    }

    async setupLayout(regionId: string) {
        try {
            this.cleanMarkers();

            this.progress.percentage = 0;

            let geoJsonBoundaryRaw = await this._dataService.getGeojsonByTypeAndRegion('boundary', regionId, {}, 
                this.progressListener.bind(this)).toPromise();
            
            this.progress.percentage = 0;

            let geoJsonTransportsRaw = await this._dataService.getGeojsonByTypeAndRegion('network_transportation', regionId, {}, 
                this.progressListener.bind(this)).toPromise();
            
            this.progress.percentage = 0;

            let geoJsonBuildings = await this._dataService.getGeojsonByTypeAndRegion('facilities_infrastructures', regionId, {}, 
                this.progressListener.bind(this)).toPromise();
  
            let features = geoJsonBoundaryRaw.data.features;
            features = features.concat(geoJsonTransportsRaw.data.features);

            geoJsonBuildings.data.features.map(feature => {
                feature['indicator'] = 'facilities_infrastructures';
                return feature;
            });

            features = features.concat(geoJsonBuildings.data.features.filter(e => e.geometry.type === 'Polygon'));

            this.geoJsonLayout = L.geoJSON(features, {
                style: this.getMapBoundaryStyle.bind(this),
                onEachFeature: this.onEachFeature.bind(this)
            });
    
            this.geoJsonLayout.addTo(this.map);
            this.map.flyTo(this.geoJsonLayout.getBounds().getCenter(), 15);
            this.setActiveMenu(this.activeMenu);
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
        this.isLegendShown = false;
        this.isToggleContext = false;

        if(this.currentDesaIndex === this.availableDesaSummaries.length - 1)
           this.currentDesaIndex = -1;
           
        this.cleanLayers();   
        this.cleanLayout();
        this.cleanMarkers();

        this.currentDesaIndex += 1; 
        this.summaries = this.availableDesaSummaries[this.currentDesaIndex];

        this.setNextPrevLabel();
        this.setupPenduduks(this.summaries.fk_region_id);
        this.setupLayout(this.summaries.fk_region_id);
    }
    
    async prev() {
        this.isLegendShown = false;
        this.isToggleContext = false;

        if(this.currentDesaIndex === 0)
           this.currentDesaIndex = this.availableDesaSummaries.length;

        this.cleanLayers();  
        this.cleanLayout();
        this.cleanMarkers();

        this.currentDesaIndex -= 1;
        this.summaries = this.availableDesaSummaries[this.currentDesaIndex];

        this.setNextPrevLabel();
        this.setupPenduduks(this.summaries.fk_region_id);
        this.setupLayout(this.summaries.fk_region_id);
    }

    async setMapApbdes() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();

        this.isPendidikanStatisticShown = false;
        this.isPekerjaanStatisticShown = false;

        let logPembangunan = await this._dataService.getGeojsonByTypeAndRegion('log_pembangunan', this.summaries.fk_region_id, {}, null).toPromise();
       
        for (let i=0; i<logPembangunan.data.features.length; i++) {
            let data = logPembangunan.data.features[i];
            let feature = data[6];
            let center = L.geoJSON(feature).getBounds().getCenter();
            let url = null;
            let name = feature.properties['name'] ? feature.properties['name'] : '';
            let label = '<strong>Pembangunan ' + name + '</strong>' 
                + '<br> Total: Rp ' + parseFloat(data[7]).toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1.")
                + '<hr>';

            let anggarans = data[4];

            for (let i=0; i<anggarans.length; i++) {
                let anggaran = anggarans[i];

                label += '<div><span>Kode Kegiatan:' + anggaran[0] + '<br> Kode Anggaran: ' + anggaran[1] + '<br> Anggaran: Rp ' 
                    + parseFloat(anggaran[2]).toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1.");
            }

            label += '</span></div>';

            let marker = null;

            if (data[3] === 'highway') {
                url = '/assets/images/asphalt.png';
                center = MapUtils.calculateCenterOfLineStrings(feature.geometry.coordinates);
            }
                
            else if (data[3] === 'amenity') {
                if (feature.properties[data[3]] === 'school') {
                    if (!isNaN(feature.properties['isced'])) {
                        let isced = parseInt(feature.properties['isced']);

                        if (isced === 0) 
                            url = '/assets/images/tx.png';
                        else if (isced === 1)
                            url = '/assets/images/sd.png';
                        else if (isced === 2) 
                            url = '/assets/images/smp.png';
                        else if (isced === 3)
                            url = '/assets/images/sma.png';
                        else if (isced === 4)
                            url = '/assets/images/pt.png';
                    }
                }
            }
            else if (data[3] === 'building') {
                if (feature.properties[data[3]] === 'house') {
                    label = '<strong>Pembangunan Rumah </strong><br> Anggaran: Rp ' + parseFloat(data[7]).toFixed(2); 
                    url = '/assets/images/house.png';
                }
            }
            
            marker = L.marker(center, {
                icon: L.icon({ 
                    iconUrl: url,
                    iconSize: [20, 20],
                })
            }).addTo(this.map).bindPopup(label).openPopup();

            this.markers.push(marker);
        }
    }
    
    async setMapSchools() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();
        
        this.isPekerjaanStatisticShown = false;

        this.markers = [];
        this.legends = [];
        
        let regionId = this.summaries.fk_region_id;

        this.setPendidikStatistic(regionId);
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('facilities_infrastructures', 
                regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = map.data;

        featureCollection.features = featureCollection.features.filter(e => e.properties.amenity 
            && e.properties.amenity === 'school' && e.properties.isced);
        
        for (let i=0; i<featureCollection.features.length; i++) {
            let feature = featureCollection.features[i];
            let center = L.geoJSON(feature).getBounds().getCenter();
            let marker = null;
            let url = null;
            let label = null;

            if (feature.properties['amenity'] && feature.properties['amenity'] === 'school') {
                if (feature.properties['isced']) {
                    if (feature.properties['isced'] == 0) {
                        url = '/assets/images/tk.png';
                        label = 'TK';
                    }
                    else if (feature.properties['isced'] == 1) {
                        url = '/assets/images/sd.png';
                        label = 'SD';
                    }
                    else if (feature.properties['isced'] == 2) {
                        url = '/assets/images/smp.png';
                        label = 'SMP';
                    }
                    else if (feature.properties['isced'] == 3) {
                        url = '/assets/images/sma.png';
                        label = 'SMA';
                    }
                    else if (feature.properties['isced'] == 4) {
                        url = '/assets/images/pt.png';
                        label = 'PT';
                    }

                    let existingLegend = this.legends.filter(e => e.url === url)[0];

                    if(!existingLegend) {
                        if (label === 'TK')
                            this.legends.push({ label: label, url: url, color: null, total: this.summaries.pemetaan_school_tk });
                        
                        else if (label === 'SD')
                            this.legends.push({ label: label, url: url, color: null, total: this.summaries.pemetaan_school_sd });
                        
                        else if (label === 'SMP')
                            this.legends.push({ label: label, url: url, color: null, total: this.summaries.pemetaan_school_smp });

                        else if (label === 'SMA')
                            this.legends.push({ label: label, url: url, color: null, total: this.summaries.pemetaan_school_sma });

                        else if (label === 'PT')
                            this.legends.push({ label: label, url: url, color: null, total: this.summaries.pemetaan_school_pt });
                    }
                        

                    marker = L.marker(center, {
                        icon: L.icon({ 
                            iconUrl: url,
                            iconSize: [20, 20],
                            shadowSize: [64, 64],
                            iconAnchor: [22, 24],
                            shadowAnchor: [4, 62],
                            popupAnchor: [-3, -76]
                        })
                    }).addTo(this.map);
        
                    this.markers.push(marker);
                }
            }
        }

        this.isLegendShown = true;
        this.isPendidikanStatisticShown = true;
    }
    
    async setMapLanduse() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();

        this.isPendidikanStatisticShown = false;

        this.markers = [];
        this.legends = [];

        let regionId = this.summaries.fk_region_id;
        
        this.setPekerjaanStatistic(regionId);
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('landuse', 
                regionId, {}, this.progressListener.bind(this)).toPromise();

        let roads = await this._dataService.getGeojsonByTypeAndRegion('network_transportation', regionId, {}, null).toPromise();

        let featureCollection = map.data;
       
        featureCollection.features = featureCollection.features.filter(e => e.properties.landuse 
            && (e.properties.landuse === 'farmland' || e.properties.landuse === 'orchard' || e.properties.landuse === 'forest'));
        
        featureCollection.features = featureCollection.features.concat(roads.data.features);
            
        this.geoJsonLanduse = L.geoJSON(featureCollection, {
            onEachFeature: this.onEachLanduseFeature.bind(this)
        });

        this.geoJsonLanduse.addTo(this.map);

        let label = null;
        let color = null;
        let textColor = null;

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

            if (feature.properties.landuse && feature.properties.landuse === 'farmland')  {
                url =  '/assets/images/pertanian.png';
                label = 'Pertanian';
                color = 'rgba(247,230,102,0.5)';
            }

            else if (feature.properties.landuse && feature.properties.landuse === 'orchard') {
                url =  '/assets/images/perkebunan.png';
                label = 'Perkebunan';
                color = 'rgba(141,198,102,0.5)';
            }

            else if (feature.properties.landuse && feature.properties.landuse === 'forest') {
                url =  '/assets/images/hutan.png';    
                label = 'Hutan';
                color = 'rgba(0,104,56,0.5)';
                textColor = 'white';
            }
               
            if (!url)
                continue;

            let existingLegend = this.legends.filter(e => e.url === url)[0];
            
            if(!existingLegend)
                this.legends.push({ label: label, url: url, color: color, textColor: textColor });
        }

        this.isLegendShown = true;
    }

    async setMapLogPembangunan() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();
        
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
        this.cleanMarkers();
        this.cleanLegends();
        this.isPekerjaanStatisticShown = false;
        this.isPendidikanStatisticShown = false;
        
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
    
    async setMapPenduduk() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();

        let regionId = this.summaries.fk_region_id;
        
        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('facilities_infrastructures', 
            regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = map.data;
            
        featureCollection.features = featureCollection.features.filter(e => e.properties.building 
            && (e.properties.building === 'house'));

        for (let i=0; i<featureCollection.features.length; i++) {
            let feature = featureCollection.features[i];
            let center = L.geoJSON(feature).getBounds().getCenter();
    
            let url = '/assets/images/house.png';

            let marker = L.marker(center, {
                icon: L.icon({ 
                    iconUrl: url,
                    iconSize: [15, 15],
                    shadowSize: [50, 64],
                    iconAnchor: [22, 24],
                    shadowAnchor: [4, 62],
                    popupAnchor: [-3, -76]
                })
            }).addTo(this.map);

            this.markers.push(marker);
        }

        this.isPekerjaanStatisticShown = false;
        this.isPendidikanStatisticShown = false;
        this.isLegendShown = false;
    }

    async setMapHighway() {
        this.cleanLayers(); 
        this.cleanMarkers();
        this.cleanLegends();

        this.isPendidikanStatisticShown = false;
        this.isPekerjaanStatisticShown = false;
        
        this.markers = [];
        this.legends = [];

        let regionId = this.summaries.fk_region_id;

        this.progress.percentage = 0;

        let map = await this._dataService.getGeojsonByTypeAndRegion('network_transportation', 
                regionId, {}, this.progressListener.bind(this)).toPromise();

        let featureCollection = map.data;
       
        featureCollection.features = featureCollection.features.filter(e => e.properties.highway || e.properties.bridge);
        
        this.geoJsonHighway = L.geoJSON(featureCollection, {
            onEachFeature: this.onEachFeature.bind(this)
        });

        this.geoJsonHighway.addTo(this.map);

        let label = null;
        let color = null;
        let textColor = null;

        for (let i=0; i<featureCollection.features.length; i++) {
            let feature = featureCollection.features[i];
            let center = MapUtils.calculateCenterOfLineStrings(feature.geometry.coordinates);
            let marker = null;
            let url = null;

            if (feature.properties.surface && feature.properties.surface === 'asphalt')  {
                url =  '/assets/images/asphalt.png';
                label = 'Aspal';
            }

            else if (feature.properties.surface && feature.properties.surface === 'concrete') {
                url =  '/assets/images/concrete.png';
                label = 'Beton';
            }

            else if (feature.properties.bridge) {
                url =  '/assets/images/bridge.png';    
                label = 'Jembatan';
            }

            else {
                url =  '/assets/images/other.png';
                label = 'Lainnya';
            }
               
            if (!url)
                continue;

            marker = MapUtils.createMarker(url, center);

            this.markers.push(marker.addTo(this.map));

            let existingLegend = this.legends.filter(e => e.url === url)[0];
            
            if(!existingLegend)
                this.legends.push({ label: label, url: url, color: color, textColor: textColor });
        }

        this.isLegendShown = true;
    }

    async setPekerjaanStatistic(regionId) {
        if (this.penduduks.length === 0)
            return;

        if(this.isToggleContext) {
            this.isPekerjaanStatisticShown = true;
            this.isPekerjaanContextShown = true;
        }
       
        let pekerjaanRaw = this.chartHelper.getPekerjaanRaw(this.penduduks);
        let pekerjaanData = this.chartHelper.transformDataStacked(pekerjaanRaw, 'pekerjaan');
        let pekerjaanChart = this.chartHelper.renderMultiBarHorizontalChart('pekerjaan', pekerjaanData);

        setTimeout(() => {
            pekerjaanChart.update();
        }, 1000);
    }

    async setPendidikStatistic(regionId) {
        if (this.penduduks.length === 0)
            return;
            
        this.isPendidikanStatisticShown = true;
        this.isPendidikanContextShown = true;
        
        let pendidikanRaw = this.chartHelper.getPendidikanRaw(this.penduduks);
        let pendidikanData = this.chartHelper.transformDataStacked(pendidikanRaw, 'pendidikan');
        let pendidikanChart = this.chartHelper.renderMultiBarHorizontalChart('pendidikan', pendidikanData);

        setTimeout(() => {
            pendidikanChart.update();
        }, 1000)
    }

    setActiveMenu(menu: string) {
        this.activeMenu = menu;

        switch(menu) {
            case 'apbdes':
                this.setMapApbdes();
            break;
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
            case 'penduduk':
                this.setMapPenduduk();
            break;
            case 'highway':
                this.setMapHighway();
            break;
        }
        return false;
    }

    getMapBoundaryStyle(feature) {
        return { color: '#aaa', weight: 1 };
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

            if (!matchedElement) { 
                if (feature['indicator']) {
                    let style = { color: 'rgb(255,165,0)', fill: 'rgb(255, 165, 0)', fillOpacity: 1, weight: 0 };
                    layer.setStyle(style);
                }
                continue;
            }

            if (matchedElement['style']) {
                let style = MapUtils.setupStyle(matchedElement['style']);
                style['weight'] = 2;
                layer['setStyle'] ? layer['setStyle'](style) : null;
            }

            if (feature.properties['boundary_sign']) { 
                let style = MapUtils.setupStyle({ dashArray: feature.properties['boundary_sign'] });
                layer.setStyle(style);
            }

            if (feature['indicator']) {
                let style = { color: 'rgb(255,165,0)', fill: 'rgb(255, 165, 0)', fillOpacity: 1, weight: 0 };
                layer.setStyle(style);
            }
        }
    }

    onEachLanduseFeature(feature, layer) {
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

                style['weight'] = 0;

                if (feature.geometry.type === 'Polygon') {
                    style['fill'] = style['color'];
                    style['fillOpacity'] =0.5; 
                }
                    
                layer['setStyle'] ? layer['setStyle'](style) : null;
            }
        }
    }

    onMapReady(map: L.Map): void {
        this.map = map;

        let satellite = L.tileLayer( 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZ2hrIiwiYSI6ImUxYmUxZDU3MTllY2ZkMGQ3OTAwNTg1MmNlMWUyYWIyIn0.qZKc1XfW236NeD0qAKBf9A')

        let basemapControl = {
        //"OSM": streets,
        "Satelit": satellite
        }

        L.control.layers( null, basemapControl, {'position': 'bottomleft'} ).addTo(this.map);
    }
   
    setNextPrevLabel() {
        this.nextDesa = this.availableDesaSummaries[this.currentDesaIndex + 1] 
            ? this.availableDesaSummaries[this.currentDesaIndex + 1].region.name : this.availableDesaSummaries[0].region.name;
    
        this.prevDesa = this.availableDesaSummaries[this.currentDesaIndex - 1] 
            ? this.availableDesaSummaries[this.currentDesaIndex - 1].region.name : this.availableDesaSummaries[this.availableDesaSummaries.length - 1].region.name;
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
    
    cleanLegends(): void {
        this.isLegendShown = false;
        this.legends = [];
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

    ngOnDestroy(): void {}
}