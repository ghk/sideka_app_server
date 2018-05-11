import * as L from 'leaflet';
import { CONFIG } from './bigConfig';

export class MapUtils {
    static createGeoJson(): any {
        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": []
        }
    }

    static createFeature(coordinates, type, properties): any {
        return {
            "type": "Feature",
            "geometry": { "coordinates": coordinates, "type": type },
            "properties": properties
        }
    }

    static setupStyle(configStyle) {
        let resultStyle = Object.assign({}, configStyle);
        let color = this.getStyleColor(configStyle);
        
        if (color)
            resultStyle['color'] = color;

        return resultStyle;
    }

    static getStyleColor(configStyle, defaultColor = null) {
        if (configStyle['cmykColor'])
            return this.cmykToRgbString(configStyle['cmykColor']);
        if (configStyle['rgbColor'])
            return this.rgbToRgbString(configStyle['rgbColor']);
        return defaultColor;
    }

    static cmykToRgbString(cmyk): any {
        let c = cmyk[0], m = cmyk[1], y = cmyk[2], k = cmyk[3];
        let r, g, b;
        r = 255 - ((Math.min(1, c * (1 - k) + k)) * 255);
        g = 255 - ((Math.min(1, m * (1 - k) + k)) * 255);
        b = 255 - ((Math.min(1, y * (1 - k) + k)) * 255);
        return "rgb(" + r + "," + g + "," + b + ")";
    }

    static rgbToRgbString(rgb): any {
        let r = rgb[0], g = rgb[1], b = rgb[2];
        return "rgb(" + r + "," + g + "," + b + ")";
    }

    static createMarker(url, center): L.Marker {
        let bigIcon = L.icon({
            iconUrl:  url,
            iconSize:     [15, 15],
            shadowSize:   [50, 64],
            iconAnchor:   [22, 24],
            shadowAnchor: [4, 62],
            popupAnchor:  [-3, -76]
        });

        return L.marker(center, {icon: bigIcon});
    }

    static calculateCenterOfLineStrings(coordinates: any[]): any {
        let x = 0;
        let y = 0;

        for (let i=0; i<coordinates.length; i++) {
            x += coordinates[i][0];
            y += coordinates[i][1];
        }

        return [y/coordinates.length, x/coordinates.length];
    }

    static onEachFeature(feature, layer): void {
        layer.on("click", function(){
            console.log(feature.properties);
        });
        for (let index in CONFIG) {
            let indicator = CONFIG[index];
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

            var strokeWeight = 2;
            if(feature.properties.landuse){
                strokeWeight = 0;
            }

            if (!matchedElement) { 
                if (feature['indicator']) {
                    let style = { color: 'rgb(255,165,0)', fill: 'rgb(255, 165, 0)', fillOpacity: 1, weight: 0, strokeWeight: strokeWeight };
                    layer.setStyle(style);
                }
                continue;
            }

            if (matchedElement['style']) {
                let style = MapUtils.setupStyle(matchedElement['style']);
                style['weight'] = strokeWeight;
                style['stroke-weight'] = strokeWeight;
                layer['setStyle'] ? layer['setStyle'](style) : null;
            }

            if (feature['indicator']) {
                let style = { color: 'rgb(255,165,0)', fill: 'rgb(255, 165, 0)', fillOpacity: 1, weight: 0 };
                layer.setStyle(style);
            }
        }

        var text = feature.properties.crop;
        if(!text)
            text = feature.properties.trees;
        if(text){
            layer.bindPopup("<span>"+text+"</span>");
        }
    }
}
