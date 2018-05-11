import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { tileLayer, Map, MapOptions, latLng, control, GeoJSON, geoJSON, divIcon, marker, icon, LatLng, Layer, LayerGroup, layerGroup } from 'leaflet';
import { ActivatedRoute } from '@angular/router';
import { DataService } from '../services/data';
import { Location } from '@angular/common';
import { DesaInstance } from './desaInstance';
import { MapUtils } from '../helpers/mapUtils';
import { length as GeoJsonLength } from '@turf/turf';

import geoJSONArea from '@mapbox/geojson-area';
import { ChartHelper } from '../helpers/chartHelper';

const LIGHT = tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png');
const SATELLITE = tileLayer('https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZ2hrIiwiYSI6ImUxYmUxZDU3MTllY2ZkMGQ3OTAwNTg1MmNlMWUyYWIyIn0.qZKc1XfW236NeD0qAKBf9A');
//const OSM = tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');

@Component({
    selector: 'st-desa',
    templateUrl: '../templates/desa.html'
})
export class DesaComponent implements OnInit, OnDestroy {
    activeDesa: DesaInstance;
    activeMenu: string;
    nextDesa: DesaInstance;
    prevDesa: DesaInstance;

    desaInstances: DesaInstance[];
    geojsonBoundary: GeoJSON;
    map: Map;
    options: MapOptions;
    chartHelper: ChartHelper;
    isLoadingData: boolean;
    loadingMessage: string;

    showPoints = true;
    labelMarkers: LayerGroup;
    pointMarkers: LayerGroup;

    constructor(private _router: ActivatedRoute, 
                private _dataService: DataService, 
                private _location: Location) {}

    ngOnInit(): void {
        this.options = { center: latLng([-2.604236, 116.499023]), zoom: 5, layers: [LIGHT] };
        this.labelMarkers = layerGroup([]);
        this.pointMarkers = layerGroup([]);
        this.chartHelper = new ChartHelper();
    }

    async load(regionId: string) {
        this.isLoadingData = true;
        this.desaInstances = [];

        let boundaries = await this._dataService.getBoundaries(null).toPromise();
       
        this.geojsonBoundary = geoJSON(boundaries.data, {
                                    onEachFeature: MapUtils.onEachFeature,
                                    style: (feature) => { return { color: "#aaa", weight: 1 } }
                                }).addTo(this.map);

        this.geojsonBoundary.eachLayer(layer => {
            let existingDesa = this.desaInstances.filter(e => e.regionId === layer['feature']['properties']['regionId'])[0];

            if (!existingDesa) {
                let instance = new DesaInstance();
                instance.regionId = layer['feature']['properties']['regionId'];
                instance.regionName = layer['feature']['properties']['regionName'];
                this.desaInstances.push(instance);
            } 
        });

        this.setDesaLabels();
        this.setDesaPoints();

        this.desaInstances.sort((a, b) => {
            if (a.regionId < b.regionId)
                return -1;
            else if (a.regionId > b.regionId)
                return  1;
        });

        this.geojsonBoundary.on('mouseover', e => {
            e['layer']['setStyle']({ color: 'blue', fill: 'transparent', weight: 1 });
        });

        this.geojsonBoundary.on('mouseout', e => {
            e['layer']['setStyle']({ color: "#aaa", weight: 1 });
        });

        this.geojsonBoundary.on('click', e => {
            let layer = e['layer'];
            let desa = this.desaInstances.filter(e => e.regionId === layer['feature']['properties']['regionId'])[0];
            this.setActiveDesa(desa)
        });

        this.activeDesa = this.desaInstances.filter(e => e.regionId === regionId)[0];
        this.setActiveDesa(this.activeDesa);
    }

    async setActiveDesa(desa: DesaInstance) {
        this.isLoadingData = true;

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);
        
        this.reset();
        this.activeDesa = desa;
        this.setNextPrev();

        if (!this.activeDesa.layout) {
            let layout = await this._dataService.getLayoutByRegion(this.activeDesa.regionId, null).toPromise();
            this.activeDesa.layout = layout.data;
        }
        
        if (!this.activeDesa.summary) {
            let summary = await this._dataService.getSummariesByRegion(this.activeDesa.regionId, {}, null).toPromise();
            this.activeDesa.summary = summary[0];
        }
 
        this.activeDesa.setActiveGeoJson();
        this.activeDesa.activeGeoJson.addTo(this.map);

        this.map.flyTo(this.activeDesa.activeGeoJson.getBounds().getCenter(), 15); 

        this.setActiveMenu(this.activeMenu);
        this.isLoadingData = false;
    }

    setActiveMenu(menu: string): boolean {
        this.activeMenu = menu;

        switch(menu) {
            case 'apbdes':
                this.setApbdesData();
            break;
            case 'boundary':
                this.setBoundaryData();
            break;
            case 'penduduk':
                this.setPendudukData();
            break;
            case 'schools':
                this.setSchoolData();
            break;
            case 'landuse':
                this.setLanduseData();
            break;
            case 'highway':
                this.setHighwayData();
            break;
        }

        return false;
    }

    setApbdesData(): void {
        this.reset();

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        this.activeDesa.activeGeoJson.addTo(this.map);

        for (let i=0; i<this.activeDesa.layout.apbdes.length; i++) {
            let data = this.activeDesa.layout.apbdes[i];
            let feature = data[6];

            if (!feature['geometry'])
                continue;

            let center = geoJSON(feature).getBounds().getCenter();
            let url = null;
            let name = feature.properties['name'] ? feature.properties['name'] : '';

            let label = '<strong>Pembangunan ' + name + '</strong>' 
                + '<br> Total: Rp ' + parseFloat(data[7]).toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1.");

            if (feature['properties']['highway']) {
                url = '/assets/images/asphalt.png';
                center = MapUtils.calculateCenterOfLineStrings(feature.geometry.coordinates);
            }
            else if (feature['properties']['amenity']) {
                if (feature['properties']['amenity'] === 'school') {
                    if (isNaN(feature['properties']['isced']))
                        continue;

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

                if (feature['properties']['amenity'] === 'place_of_worship') {
                    url = '/assets/images/house.png';
                }
            }
            else if (feature['properties']['building']) {
                if (feature['properties']['building'] === 'house') {
                    label = '<strong>Pembangunan Rumah </strong><br> Anggaran: Rp ' + parseFloat(data[7]).toFixed(2); 
                    url = '/assets/images/house.png';
                }
            }

            let apbdesMarker = marker(center, {
                icon: icon({ 
                    iconUrl: url,
                    iconSize: [20, 20],
                })
            }).addTo(this.map).bindPopup(label, { autoClose: false }).openPopup();

            this.activeDesa.apbdesMarkers.push(apbdesMarker);
        }
    }

    setBoundaryData(): void {
        this.reset();  
        
        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        let dusuns = this.activeDesa.layout.boundaries.filter(e => e.properties['admin_level'] && e.properties['admin_level'] === 8);
        
        for (let i=0; i<dusuns.length; i++) {
            let area = geoJSONArea.geometry(dusuns[i].geometry);

            let dusunMarker = marker(geoJSON(dusuns[i]).getBounds().getCenter(), {
                icon: divIcon({
                    className: 'label', 
                    html: '<h4 style="color: blue;"><strong>' + (area / 10000).toFixed(2) + ' Ha </strong></h4>',
                    iconSize: [30, 30]
                  })
            }).addTo(this.map);

            this.activeDesa.dusunMarkers.push(dusunMarker);
        }

        if (dusuns.length === 0) {
            let desas = this.activeDesa.layout.boundaries.filter(e => e.properties['admin_level'] && e.properties['admin_level'] === 7);
            let area = 0;

            for (let i=0; i<desas.length; i++) {
                area +=  geoJSONArea.geometry(desas[i].geometry);
            }
            
            let dusunMarker = marker(geoJSON(desas[0]).getBounds().getCenter(), {
                icon: divIcon({
                    className: 'label', 
                    html: '<h4 style="color: blue;"><strong>' + (area / 10000).toFixed(2) + ' Ha </strong></h4>',
                    iconSize: [30, 30]
                  })
            }).addTo(this.map);

            this.activeDesa.dusunMarkers.push(dusunMarker);
        }

        this.activeDesa.setBoundaryGeoJson();

 
        this.activeDesa.boundaryGeoJson.addTo(this.map);

        this.activeDesa.boundaryGeoJson.eachLayer(layer => {
            if (layer['feature'].properties['admin_level'] && layer['feature'].properties['status']) {
                if (layer['feature'].properties['status'] === 'indicative')
                    layer['setStyle'](MapUtils.setupStyle({ dashArray: 2.5}));
                else
                    layer['setStyle'](MapUtils.setupStyle({ dashArray: 0}));
            }
        });
    }

    setPendudukData(): void {
        this.reset();

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        this.activeDesa.activeGeoJson.addTo(this.map);

        for (let i=0; i<this.activeDesa.layout.houses.length; i++) {
            let feature = this.activeDesa.layout.houses[i];
            let center = geoJSON(feature).getBounds().getCenter();
            let url = '/assets/images/house.png';

            let houseMarker = marker(center, {
                icon: icon({ 
                    iconUrl: url,
                    iconSize: [15, 15],
                    shadowSize: [50, 64],
                    iconAnchor: [22, 24],
                    shadowAnchor: [4, 62],
                    popupAnchor: [-3, -76]
                })
            }).addTo(this.map);

            this.activeDesa.houseMarkers.push(houseMarker);
        }
    }

    setSchoolData(): void {
        this.reset();

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        this.activeDesa.activeGeoJson.addTo(this.map);
       
        for (let i=0; i<this.activeDesa.layout.schools.length; i++) {
            let feature = this.activeDesa.layout.schools[i];
            let center = geoJSON(feature).getBounds().getCenter();
            let url = null;
            let label = null;

            if (feature.properties['amenity'] === 'school' && feature.properties['isced']) {
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

                let existingLegend = this.activeDesa.legends.filter(e => e.url === url)[0];

                if(!existingLegend) {
                    if (label === 'TK')
                        this.activeDesa.legends.push({ label: label, url: url, color: null, total: this.activeDesa.summary.pemetaan_school_tk });
                    
                    else if (label === 'SD')
                        this.activeDesa.legends.push({ label: label, url: url, color: null, total: this.activeDesa.summary.pemetaan_school_sd });
                    
                    else if (label === 'SMP')
                        this.activeDesa.legends.push({ label: label, url: url, color: null, total: this.activeDesa.summary.pemetaan_school_smp });

                    else if (label === 'SMA')
                        this.activeDesa.legends.push({ label: label, url: url, color: null, total: this.activeDesa.summary.pemetaan_school_sma });

                    else if (label === 'PT')
                        this.activeDesa.legends.push({ label: label, url: url, color: null, total: this.activeDesa.summary.pemetaan_school_pt });
                }

                let popupContent = '<strong>' + label + '</strong><br>';
                let name = feature['name'] ? feature['name'] : 'Belum Terisi';
                let capacity = feature['capacity'] ? feature['capacity'] + ' Orang' : 'Belum Terisi';
                let address = feature['address'] ? feature['address'] : 'Belum Terisi';

                popupContent += '<span>Nama: ' + name + '<br> Kapasitas: ' + capacity + '<br>Alamat: ' + address +  '</span>';

                let schoolMarker = marker(center, {
                    icon: icon({ 
                        iconUrl: url,
                        iconSize: [20, 20]
                    })
                }).addTo(this.map);
    
                this.activeDesa.schoolMarkers.push(schoolMarker);
            }
        }

        let statData = this.activeDesa.layout.properties.statistics.pendidikan;
        let stacked = this.chartHelper.transformDataStacked(statData, 'pendidikan');
        let chartA = this.chartHelper.renderMultiBarHorizontalChart('pendidikan', stacked);

        this.activeDesa.isLegendShown = true;
        this.activeDesa.isPendidikanStatisticHidden = false;
        this.activeDesa.isPendidikanStatisticShown = true;

        setTimeout(() => {
            chartA.update();
        }, 1000)
    }

    setLanduseData(): void {
        this.reset();

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        if (this.activeDesa.landuseGeoJson)
            this.map.removeLayer(this.activeDesa.landuseGeoJson);

        this.activeDesa.setLanduseGeoJson();
        this.activeDesa.landuseGeoJson.addTo(this.map);
       
        for (let i=0; i<this.activeDesa.layout.landuses.length; i++) {
            let feature = this.activeDesa.layout.landuses[i];
            let center = geoJSON(feature).getBounds().getCenter();
            let url = null;
            let label = null;
            let color = null;
            let textColor = null;

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

            let existingLegend = this.activeDesa.legends.filter(e => e.url === url)[0];
            
            if(!existingLegend)
                this.activeDesa.legends.push({ label: label, url: url, color: color, textColor: textColor });
        }

        let statData = this.activeDesa.layout.properties.statistics.pekerjaan;
        let stacked = this.chartHelper.transformDataStacked(statData, 'pekerjaan');
        let chartB = this.chartHelper.renderMultiBarHorizontalChart('pekerjaan', stacked);
        
        this.activeDesa.isLegendShown = true;
        this.activeDesa.isPekerjaanStatisticHidden = false;
        this.activeDesa.isPekerjaanStatisticShown = true;
     
        setTimeout(() => {
            chartB.update();
        }, 1000)
    }

    setHighwayData(): void {
        this.reset();

        if (this.activeDesa.activeGeoJson)
            this.map.removeLayer(this.activeDesa.activeGeoJson);

        for (let i=0; i<this.activeDesa.layout.highways.length; i++) {
            let feature = this.activeDesa.layout.highways[i];
            let center = MapUtils.calculateCenterOfLineStrings(feature.geometry.coordinates);
            let url = null;
            let label = null;
            let color = null;
            let textColor = null;

            if (feature.properties.surface && feature.properties.surface === 'asphalt')  {
                url =  '/assets/images/aspal.png';
                label = 'Aspal';
            }
            else if (feature.properties.surface && feature.properties.surface === 'concrete') {
                url =  '/assets/images/beton.png';
                label = 'Beton';
            }
            else if (feature.properties.bridge) {
                url =  '/assets/images/bridge.png';    
                label = 'Jembatan';
            }
            else {
                url =  '/assets/images/lainnya.png';
                label = 'Lainnya';
            }
               
            if (!url)
                continue;

            let length = GeoJsonLength(feature.geometry, {units: 'kilometers'}).toFixed(2);
            let popupContent = '<strong>' + label + '</strong>' + '<p>Panjang: ' + length + ' Km';

            let highwayMarker = marker(center, {
                icon: icon({ 
                    iconUrl: url,
                    iconSize: [20, 20]
                })
            }).bindPopup(popupContent);
            
            this.activeDesa.highwayMarkers.push(highwayMarker.addTo(this.map));

            let existingLegend = this.activeDesa.legends.filter(e => e.url === url)[0];
            
            if(!existingLegend)
                this.activeDesa.legends.push({ label: label, url: url, color: color, textColor: textColor });
        }

        this.activeDesa.isLegendShown = true;
    }

    setDesaLabels(): void {
        this.labelMarkers.clearLayers();

        this.geojsonBoundary.eachLayer(layer => {
           let labelMarker = marker(geoJSON(layer['feature']).getBounds().getCenter(), {
                icon: divIcon({
                    className: 'label', 
                    html: '<span style="color: blue;">' + layer['feature']['properties']['regionName'] + ' </span>',
                    iconSize: [30, 30]
                  })
            });

            this.labelMarkers.addLayer(labelMarker);
        })
    }

    setDesaPoints(): void {
        this.pointMarkers.clearLayers();

        this.geojsonBoundary.eachLayer(layer => {
            let center = geoJSON(layer['feature']).getBounds().getCenter();
            let popupContent = '<strong>' + layer['feature']['properties']['regionName'] + '</strong>';

            let pointMarker = marker(center, {
                icon: icon({ 
                    iconUrl: '/assets/images/titikdesa-01.png',
                    iconSize: [20, 20],
                })
            }).bindPopup(popupContent).openPopup();

           this.pointMarkers.addLayer(pointMarker);
        })
    }

    setNextPrev(): void {
        let index = this.desaInstances.indexOf(this.activeDesa);

        this.nextDesa = this.desaInstances[index + 1 > this.desaInstances.length - 1 ? 0 : index + 1];
        this.prevDesa = this.desaInstances[index - 1 < 0 ? this.desaInstances.length - 1 : index - 1];
    }

    setLocation(desa): void {
        this.setActiveDesa(desa);
        this._location.replaceState('/desa/region/' + desa.regionId);
    }

    reset(): void {
        this.activeDesa.isPendidikanStatisticShown = false;
        this.activeDesa.isLegendShown = false;
        this.activeDesa.isPekerjaanStatisticShown = false;
        this.activeDesa.isPekerjaanStatisticHidden = false;

        this.activeDesa.clearMarkers(this.map);

        if (this.activeDesa.landuseGeoJson)
            this.map.removeLayer(this.activeDesa.landuseGeoJson);

        if (this.activeDesa.boundaryGeoJson)
            this.map.removeLayer(this.activeDesa.boundaryGeoJson);
    }

    recenter(): boolean {
        this.map.flyTo(this.activeDesa.activeGeoJson.getBounds().getCenter(), 15);
        return false;
    }

    onMapReady(map: Map) {
        this.map = map;

        control.layers(null, {"Satelit": SATELLITE, "Light": LIGHT}, {'position': 'bottomleft'}).addTo(this.map);

        this._router.params.subscribe(
            params => {
                this.load(params['regionId']);
            } 
        );

        console.log("on map ready");
        this.pointMarkers.addTo(this.map);
        this.showPoints = true;

        this.map.on('zoomend', e => {
            let zoom = e.target["_zoom"];
            console.log("zoom end", zoom);
            if (zoom >= 10){
                if(this.showPoints){
                    console.log("show label");
                    this.labelMarkers.addTo(this.map);
                    this.map.removeLayer(this.pointMarkers);
                    this.showPoints = false;
                }
            } else {
                if(!this.showPoints){
                    console.log("show points");
                    this.pointMarkers.addTo(this.map);
                    this.map.removeLayer(this.labelMarkers);
                    this.showPoints = true;
                }
            }
        });
    }

    ngOnDestroy(): void {}
}
