import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';

import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';

@Component({
    selector: 'st-map',
    templateUrl: '../templates/map.html',
})
export class MapComponent implements OnInit, OnDestroy {

    leafletOptions: any;
    leafletLayers: L.Layer[];
    map: L.Map;

    @ViewChild('map')
    leafletComponent: ngxLeaflet.LeafletDirective

    constructor() { }

    ngOnInit(): void {
        this.leafletOptions = {
            layers: [
                L.tileLayer('http://a.basemaps.cartocdn.com/light_nolabels/{z}/{y}/{x}.png', {
                    maxZoom: 18,
                    attribution: '',
                    id: 'mapbox.streets'
                })
            ],
            zoom: 5,
            center: L.latLng([-0.7893, 113.9213])
        }
    }

    ngOnDestroy(): void { }

    onMapReady(map): void {
        this.map = map;
    }
}
