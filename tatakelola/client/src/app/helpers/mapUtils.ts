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

     static getCentroid(data): any[] {
        let result = [0, 0];

        if(data.length === 0)
            return result;

        let xCoordinates = [];
        let yCoordinates = [];
        let geometries = data.map(e => e.geometry);
        let coordinates = geometries.map(e => e.coordinates);

        for(let i=0; i<coordinates.length; i++){
            if(coordinates[i][0] instanceof Array) {
                 for(let j=0; j<coordinates[i].length; j++) {
                    if(coordinates[i][j][0] instanceof Array) {
                         for(let k=0; k<coordinates[i][j].length; k++) {
                            xCoordinates.push(parseFloat(coordinates[i][j][k][0]));
                            yCoordinates.push(parseFloat(coordinates[i][j][k][1]));
                         }
                    }
                    else {
                         xCoordinates.push(parseFloat(coordinates[i][j][0]));
                         yCoordinates.push(parseFloat(coordinates[i][j][1]));
                     }
                 }
            }
            else {
                xCoordinates.push(parseFloat(coordinates[i][0]));
                yCoordinates.push(parseFloat(coordinates[i][1]));
            }
        }

        let minX = Math.min.apply(null, xCoordinates);
        let maxX = Math.max.apply(null, xCoordinates);
        let minY = Math.min.apply(null, yCoordinates);
        let maxY = Math.min.apply(null, yCoordinates);
        let centroid = [(maxX + minX) /2, (maxY + minY)/2];
        return centroid;
    }

}
