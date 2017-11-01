import simplejson as json
import geojson


class PemetaanContentTransformer:
    @staticmethod
    def transform(content):
        serialized_content = json.loads(content)
        columns = {}
        result = {}

        for column in serialized_content['columns'].keys():
            columns[column] = serialized_content['columns'][column]
            result[column] = []
            for data in serialized_content['data'][column]:
                del data['id']
                del data['indicator']
                result[column].append(data)

        return result


class GeojsonTransformer():
    @staticmethod
    def transform(data):
        features = []
        for datum in data:
            feature = geojson.loads(json.dumps(datum))
            features.append(feature)
        result = geojson.FeatureCollection(features)
        return result
