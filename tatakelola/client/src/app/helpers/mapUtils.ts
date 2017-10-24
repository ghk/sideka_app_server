export default class MapUtils {
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
            "geometry": {"coordinates": coordinates, "type": type},
            "properties": properties
        }
    }

     static setupStyle(configStyle){
        let resultStyle = Object.assign({}, configStyle);
        let color = this.getStyleColor(configStyle);
        if(color)
            resultStyle['color'] = color;
        return resultStyle;
    }

    static getStyleColor(configStyle, defaultColor=null){
        if(configStyle['cmykColor'])
            return this.cmykToRgbString(configStyle['cmykColor']);
        if(configStyle['rgbColor'])
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

    static getCentroid(coordinates): any[] {
        let result = [0, 0];

        if(coordinates.length === 0)
            return result;

        let xCoordinates = [];
        let yCoordinates = [];
       
        for(let i=0; i<coordinates.length; i++){
            let coordinate = coordinates[i];

            for(let j=0; j<coordinate.length; j++){
                if(coordinate[j][0] instanceof Array){
                    for(let k=0; k<coordinate[j].length; k++){
                        xCoordinates.push(coordinate[j][k][0]);
                        yCoordinates.push(coordinate[j][k][1]);
                    }
                }
                else{
                    xCoordinates.push(coordinate[j][0]);
                    yCoordinates.push(coordinate[j][1]);
                }
            }
        }

        let xLength = xCoordinates.length;
        let yLength = yCoordinates.length;

        let sumX = xCoordinates.reduce((a, b) => { return a + b; });
        let sumY = yCoordinates.reduce((a, b) => { return a + b; });
        
        result[0] = sumX /xLength;
        result[1] = sumY /yLength;

        return result;
    }

}
