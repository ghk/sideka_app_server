import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';

import * as ngxLeaflet from '@asymmetrik/ngx-leaflet';
import * as L from 'leaflet';
import * as $ from 'jquery';

@Component({
     selector: 'desa',
     templateUrl: '../templates/desa.html'
})

export class DesaComponent implements OnInit, OnDestroy { 
    leafletOptions: any;
    isStatisticShown: boolean;
    isSidebarShown: boolean;

    constructor() {}

    ngOnInit(): void {
       this.isStatisticShown = false;
       this.isSidebarShown = true;
       this.leafletOptions = {
            layers: [
                L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
                    maxZoom: 18,
                    attribution: '',
                    id: 'mapbox.streets'
                })
            ],
            zoom: 12,
            center: L.latLng([1.0470057, 102.7549526])
        }      

        $('.leaflet-control-zoom').css({display: 'none'});
    }

    ngOnDestroy(): void {}
}
