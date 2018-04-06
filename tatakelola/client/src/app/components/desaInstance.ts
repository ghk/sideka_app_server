import { GeoJSON, geoJSON } from 'leaflet';

import { MapUtils } from '../helpers/mapUtils';

export class DesaInstance {
    index: number;
    regionId: any;
    regionName: string;
    summary: any;
    layout: any;
    inactiveGeoJson: GeoJSON;
    activeGeoJson: GeoJSON;
    landuseGeoJson: GeoJSON;
    boundaryGeoJson: GeoJSON;
    highwayGeoJson: GeoJSON;
    apbdesMarkers: any[];
    dusunMarkers: any[];
    houseMarkers: any[];
    schoolMarkers: any[];
    highwayMarkers: any[];
    legends: any[];
    isLegendShown: boolean;
    isPendidikanStatisticShown: boolean;
    isPendidikanStatisticHidden: boolean;
    isPekerjaanStatisticShown: boolean;
    isPekerjaanStatisticHidden: boolean;

    constructor() {
        this.apbdesMarkers = [];
        this.dusunMarkers = [];
        this.houseMarkers = [];
        this.schoolMarkers = [];
        this.highwayMarkers = [];
        this.legends = [];
        this.isLegendShown = false;
        this.isPendidikanStatisticHidden = false;
        this.isPendidikanStatisticShown = false;
        this.isPekerjaanStatisticShown = false;
        this.isPekerjaanStatisticHidden = false;
    }

    setActiveGeoJson() {
        this.activeGeoJson = geoJSON(this.layout.base, {
            onEachFeature: MapUtils.onEachFeature,
            style: (feature) => { return { color: "#aaa", weight: 1 } }
        });
    }

    setBoundaryGeoJson() {
        this.boundaryGeoJson = geoJSON(this.layout.boundaries, {
            onEachFeature: MapUtils.onEachFeature,
            style: (feature) => { return { color: "#aaa", weight: 1 } }
        });
    }

    setLanduseGeoJson() {
        this.landuseGeoJson = geoJSON(this.layout.landuses, {
            onEachFeature: MapUtils.onEachFeature,
            style: (feature) => { return { color: "#aaa", weight: 1 } }
        });
    }

    setHighwayGeoJson() {
        this.highwayGeoJson = geoJSON(this.layout.highways, {
            onEachFeature: MapUtils.onEachFeature,
            style: (feature) => { return { color: "#aaa", weight: 1 } }
        });
    }

    clearMarkers(map) {
        for (let i=0; i<this.apbdesMarkers.length; i++) {
            map.removeLayer(this.apbdesMarkers[i]);
        }

        for (let i=0; i<this.dusunMarkers.length; i++) {
            map.removeLayer(this.dusunMarkers[i]);
        }

        for (let i=0; i<this.houseMarkers.length; i++) {
            map.removeLayer(this.houseMarkers[i]);
        }

        for (let i=0; i<this.schoolMarkers.length; i++) {
            map.removeLayer(this.schoolMarkers[i]);
        }

        for (let i=0; i<this.highwayMarkers.length; i++) {
            map.removeLayer(this.highwayMarkers[i]);
        }
        
        this.apbdesMarkers = [];
        this.dusunMarkers = [];
        this.houseMarkers = [];
        this.schoolMarkers = [];
        this.highwayMarkers = [];
        this.legends = [];
    }
}