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
    map: L.Map;

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

        $('.leaflet-control-zoom').css({display: 'none'});
    }

    ngOnDestroy(): void {}

    onMapReady(map: L.Map): void {
       this.map = map;
       this.loadMapData();
    }

    loadMapData(): void {
       this.http.get('assets/data.json').map(res => res.json()).subscribe(
           result => {
               let data = MapUtils.createGeoJson();
               data.features.push(result.batas.desa[0]);

               let options = {
                 style: (feature) => {
                      return { color: '#000', weight: feature.geometry.type === 'LineString' ? 3 : 1 }
                  },
               };
               this.geojsonData = L.geoJSON(data, options).addTo(this.map);
           },
           error => {}
       )
    }
}
