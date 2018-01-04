import * as L from 'leaflet';

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
            iconUrl: 'assets/markers/' + url,
            iconSize:     [15, 15],
            shadowSize:   [50, 64],
            iconAnchor:   [22, 24],
            shadowAnchor: [4, 62],
            popupAnchor:  [-3, -76]
        });

        return L.marker(center, {icon: bigIcon});
    }
}
