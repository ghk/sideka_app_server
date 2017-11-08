import simplejson as json
import geojson


class ContentTransformer:
    @staticmethod
    def transform(content):
        serialized_content = json.loads(content)
        columns = {}
        result = {}

        if (type(serialized_content['columns']) is list):
            # TODO: LOG
            return None

        for column in serialized_content['columns'].keys():
            columns[column] = serialized_content['columns'][column]
            result[column] = []
            for data in serialized_content['data'][column]:
                obj = dict.fromkeys(columns[column])
                for index, datum in enumerate(data):
                    obj[columns[column][index]] = datum
                result[column].append(obj)

        return result


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
