import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { Http } from '@angular/http';

import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';
import * as $ from 'jquery';

import 'rxjs/add/operator/map';

import MapUtils from '../helpers/mapUtils';

@Component({
     selector: 'desa',
     templateUrl: '../templates/desa.html'
})
export class DesaComponent implements OnInit, OnDestroy { 
    leafletOptions: any;
    isStatisticShown: boolean;
    isSidebarShown: boolean;
    geojsonData: L.GeoJSON;
    geojsonOptions: any;
    map: L.Map;
    mapData: any;
    mapLayout: any[];
    bigConfig: any;

    constructor(private http:Http) {}

    ngOnInit(): void {
       this.isStatisticShown = false;
       this.isSidebarShown = true;
       this.leafletOptions = {
            layers: [
                L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
            ],
            zoom: 14,
            center: L.latLng([-7.547389769590928, 108.21044272398679])
        }      
  
       this.geojsonOptions = {
          style: (feature) => {
              return { color: '#000', weight: feature.geometry.type === 'LineString' ? 3 : 1 }
          },

          onEachFeature: (feature, layer) => {
              let indicators = this.bigConfig;

              for(let i=0; i<indicators.length; i++) { 
                  let indicator = indicators[i];
                  let element = null;

                  for(let j=0; j<indicator.elements.length; j++) {
                      let current = indicator.elements[j];

                    if(current.values){
                        let valueKeys = Object.keys(current.values);
                        if(valueKeys.every(valueKey => feature["properties"][valueKey] === current.values[valueKey])){
                            element = current;
                            break;
                        }
                    }
                  }

                  if (!element)
                    return;

                  if (element['style']) {
                    let style = MapUtils.setupStyle(element['style']);
                    layer.setStyle(style);
                  }
              }
          }
       }

       this.loadBigConfig();
       this.loadMapData();
       this.loadMapLayout();

       $('.leaflet-control-zoom').css({display: 'none'});
    }
    
    loadMapLayout(): void {
        this.http.get('assets/mapLayout.json').map(res => res.json()).subscribe(
           result => {
              this.mapLayout = result;
           },
           error => {}
        )
    }

    loadMapData(): void {
        this.http.get('assets/mapData.json').map(res => res.json()).subscribe(
           result => {
              this.mapData = result;
           },
           error => {}
        )
    }

    loadBigConfig(): void {
        this.http.get('assets/bigConfig.json').map(res => res.json()).subscribe(
            result => {
               this.bigConfig = result;
            },
            error => {}
        );
    }

    //Dummy method to get map layout
    extractData(): void {
       this.http.get('assets/pemetaan.json').map(res => res.json()).subscribe(
          result => {
             let indicators = Object.keys(result.data).filter(e => e !== 'log_pembangunan');
             let mapLayout = [];

             indicators.forEach(indicator => {
                 mapLayout = mapLayout.concat(result.data[indicator]);
             });
          },
          error => {}
       )
    }

    ngOnDestroy(): void {}

    onMapReady(map: L.Map): void {
       this.map = map;
    }

    setMapData(type): boolean {
       this.clearMap();
       let geojson = MapUtils.createGeoJson();

       switch(type) {
          case 'pembangunan':
            break;
          case 'batas':
            for(let i=0; i<this.mapData.batas.length; i++) {
               let data = this.mapData.batas[i];
               let feature = this.mapLayout.filter(e => e.id == data.spatialId)[0];

               geojson.features.push(feature);
            }
            break;
          case 'potensi': 
            for(let i=0; i<this.mapData.potensi.length; i++) {
               let data = this.mapData.potensi[i];
               let feature = this.mapLayout.filter(e => e.id == data.spatialId)[0];

               geojson.features.push(feature);
            }
            break;
       }

       this.geojsonData = L.geoJSON(geojson, this.geojsonOptions).addTo(this.map);

       return false;
    }
    
    clearMap() {
        this.geojsonData ? this.map.removeLayer(this.geojsonData) : null;
    }
}
