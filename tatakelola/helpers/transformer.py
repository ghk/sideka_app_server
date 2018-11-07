import logging
import simplejson as json
import geojson
import math

from math import pi, cos, sqrt
from tatakelola.models import Summary, PendudukReference
from area import area
from datetime import date

logger = logging.getLogger('tatakelola')

sources = {
    "genders": [], 
    "pekerjaan": ["Petani", "Pedagang", "Karyawan", "Nelayan", "Lainnya"], 
    "pendidikan": ["Tamat SD", "Tamat SMP", "Tamat SMA", "Tamat PT"] 
}

pendidikan_groups = {
    "Tidak Diketahui": ['Tidak Diketahui', 'Belum masuk TK/Kelompok Bermain', 'Tidak dapat membaca dan menulis huruf Latin/Arab','Tidak pernah sekolah',
    'Tidak tamat SD/sederajat', 'Sedang SD/sederajat'],
    "Tamat SD": ['Tamat SD/sederajat', 'Sedang SLTP/sederajat'],
    "Tamat SLTP": ['Tamat SLTP/sederajat', 'Sedang SLTA/sederajat'],
    "Tamat SLTA": ['Tamat SLTA/sederajat', 'Sedang D-1/sederajat', 'Sedang D-2/sederajat', 'Sedang D-3/sederajat',
    'Sedang D-4/sederajat', 'Sedang S-1/sederajat'],
    "Tamat PT": ['Tamat D-1/sederajat', 'Tamat D-2/sederajat', 'Tamat D-3/sederajat', 'Tamat D-4/sederajat',
    'Tamat S-1/sederajat', 'Sedang S-2/sederajat', 'Tamat S-2/sederajat', 'Sedang S-3/sederajat',
    'Tamat S-3/sederajat']
}

penduduk_range = {
    "0_15": [0, 15],
    "15_25": [15, 25],
    "25_35": [25, 35],
    "35_45": [35, 45],
    "45_55": [45, 55],
    "55_65": [55, 65],
    "65": [65, 100]
}

class ContentTransformer:
    @staticmethod
    def transform(content):
        serialized_content = content
        columns = {}
        result = {}

        if (not 'columns' in serialized_content):
            return None

        if (type(serialized_content['columns']) is list):
            # TODO: LOG?
            return None

        for column in serialized_content['columns'].keys():
            columns[column] = serialized_content['columns'][column]
            result[column] = []
            for data in serialized_content['data'][column]:
                if (not isinstance(data, list)):
                    return None
                if (len(data) != len(columns[column])):
                    return None
                obj = dict.fromkeys(columns[column])
                for index, datum in enumerate(data):
                    obj[columns[column][index]] = datum
                result[column].append(obj)

        return result


class PemetaanContentTransformer:
    @staticmethod
    def transform(content):
        serialized_content = content
        columns = {}
        result = {}

        for column in serialized_content['columns'].keys():
            columns[column] = serialized_content['columns'][column]
            result[column] = []
            for data in serialized_content['data'][column]:
                if isinstance(data, dict) == True:
                    if data.has_key('indicator'):
                        del data['indicator']

                result[column].append(data)

        return result


class GeojsonTransformer:
    @staticmethod
    def transform(data):
        features = []

        for datum in data:
            feature = geojson.loads(json.dumps(datum))
            features.append(feature)
        result = geojson.FeatureCollection(features)
        
        return result


class SummaryPendudukTransformer:
    @staticmethod
    def transform(summary, penduduks):
        summary.penduduk_sex_male = 0
        summary.penduduk_sex_female = 0
        summary.penduduk_sex_unknown = 0
        summary.penduduk_edu_none = 0
        summary.penduduk_edu_sd = 0
        summary.penduduk_edu_smp = 0
        summary.penduduk_edu_sma = 0
        summary.penduduk_edu_pt = 0
        summary.penduduk_job_petani = 0
        summary.penduduk_job_pedagang = 0
        summary.penduduk_job_karyawan = 0
        summary.penduduk_job_nelayan = 0
        summary.penduduk_job_lain = 0
        
        ref = PendudukReference()
        for penduduk in penduduks:
            if penduduk.jenis_kelamin == 'Laki-Laki':
                summary.penduduk_sex_male += 1
            elif penduduk.jenis_kelamin == 'Perempuan':
                summary.penduduk_sex_female += 1
            elif penduduk.jenis_kelamin == 'Tidak Diketahui':
                summary.penduduk_sex_unknown += 1

            group = 'Tidak Diketahui'
            for key, value in ref.pendidikan_group.items():
                if penduduk.pendidikan in value:
                    group = key
                    break

            if group == 'Tidak Diketahui':
                summary.penduduk_edu_none += 1
            elif group == 'Tamat SD':
                summary.penduduk_edu_sd += 1
            elif group == 'Tamat SLTP':
                summary.penduduk_edu_smp += 1
            elif group == 'Tamat SLTA':
                summary.penduduk_edu_sma += 1
            elif group == 'Tamat PT':
                summary.penduduk_edu_pt += 1

            pekerjaan = str(penduduk.pekerjaan)

            if pekerjaan == 'Petani':
                summary.penduduk_job_petani += 1
            elif pekerjaan.startswith('Pedagang'):
                summary.penduduk_job_pedagang += 1
            elif pekerjaan.startswith('Karyawan'):
                summary.penduduk_job_karyawan += 1
            elif pekerjaan.startswith('Nelayan'):
                summary.penduduk_job_nelayan += 1
            else:
                summary.penduduk_job_lain += 1

        return summary

class SummaryApbdesTransformer:
    @staticmethod
    def transform(summary, apbdes):

        summary.penganggaran_budgeted_revenue = 0

        for apbdes_item in enumerate(apbdes):
            print apbdes_item[1].budgeted_revenue
            summary.penganggaran_budgeted_revenue = apbdes_item[1].budgeted_revenue
            summary.penganggaran_year = apbdes_item[1].year
            break

        return summary

class SummaryGeojsonTransformer:
    @staticmethod
    def transform(summary, data, type):
        features = data['features']

        return ParsePemetaanData.parse(features, type, summary)

class ParsePemetaanData:
    @staticmethod
    def parse(features, type, summary):
        farmland_trees = []
        orchard_orchards = []
        forest_trees = []
        
        for feature in features:
            if feature.has_key('properties') == False or feature['geometry'] == None:
                if type == 'network_transportation' and feature['geometry'] != None:
                    summary.pemetaan_highway_other_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                    continue
                else:
                    continue

            properties = feature['properties']
        
            if type == 'boundary':
                if feature['geometry']['type'] != 'Polygon':
                    continue
                if feature['properties'].has_key('admin_level') == False:
                    continue
                if feature['properties']['admin_level'] == 7:
                    summary.pemetaan_desa_boundary += area(feature['geometry'])
                    summary.pemetaan_desa_circumference += 0
                elif feature['properties']['admin_level'] == 8:
                    summary.pemetaan_dusun_total += 1
            elif type == 'landuse':
                if properties.has_key('landuse') == False:
                    continue
                if properties['landuse'] == 'farmland':
                    summary.pemetaan_landuse_farmland += 1
                    if properties.has_key('farmland'):
                        farmland_trees.append(properties['farmland'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_landuse_farmland_area += area(feature['geometry'])
                elif properties['landuse'] == 'orchard':
                    summary.pemetaan_landuse_orchard += 1
                    if properties.has_key('forest'):
                        orchard_orchards.append(properties['forest'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_landuse_orchard_area += area(feature['geometry'])
                elif properties['landuse'] == 'forest':
                    summary.pemetaan_landuse_forest += 1
                    if properties.has_key('forest'):
                        forest_trees.append(properties['forest'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_landuse_forest_area += area(feature['geometry'])
            elif type == 'facilities_infrastructures':
                if properties.has_key('building'):
                    if properties.has_key('house'):
                        if properties.has_key('electricity_watt'):
                            if math.isnan(properties['electricity_watt']) == False:
                                if int(properties['electricity_watt']) > 0:
                                    summary.pemetaan_electricity_house += 1

                elif properties.has_key('amenity'): 
                    if properties['amenity'] == 'school':  
                        if properties.has_key('isced') == False:
                            continue
                        
                        isced = int(properties['isced'])

                        if isced == 0:
                            summary.pemetaan_school_tk += 1
                        elif isced == 1:
                            summary.pemetaan_school_sd += 1
                        elif isced == 2:
                            summary.pemetaan_school_smp += 1
                        elif isced == 3:
                            summary.pemetaan_school_sma += 1
                        elif isced == 4:
                            summary.pemetaan_school_pt += 1
            elif type == 'network_transportation':
                 if properties.has_key('highway') or properties.has_key('bridge'):
                     if properties.has_key('surface') == False:
                         summary.pemetaan_highway_other_length = 0
                     elif properties.has_key('bridge'):
                         if feature['geometry']['type'] == 'LineString':
                            summary.pemetaan_bridge_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                         elif feature['geometry']['type'] == 'Polygon':
                             summary.pemetaan_bridge_length = 0
                     elif properties['surface'] == 'asphalt':
                         if feature['geometry']['type'] == 'LineString':
                            summary.pemetaan_highway_asphalt_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                         elif feature['geometry']['type'] == 'Polygon':
                            summary.pemetaan_highway_asphalt_length = 0
                     elif properties['surface'] == 'concrete':
                         if feature['geometry']['type'] == 'LineString':
                            summary.pemetaan_highway_concrete_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                         elif feature['geometry']['type'] == 'Polygon':
                            summary.pemetaan_highway_concrete_length = 0
                     else:
                         if feature['geometry']['type'] == 'LineString':
                            summary.pemetaan_highway_other_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                         elif feature['geometry']['type'] == 'Polygon':
                            summary.pemetaan_highway_other_length = 0
                 else:
                    if feature['geometry']['type'] == 'LineString':
                        summary.pemetaan_highway_other_length += GeoJsonUtils.calculate_length(feature['geometry']['coordinates'])
                    elif feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_highway_other_length = 0

        return summary

class GeoJsonUtils:
    @staticmethod
    def calculate_length(coordinates):
        if len(coordinates) < 2:
            return 0
        
        result = 0
        index = 1

        for coordinate in coordinates:
            if index < len(coordinates):
                result += GeoJsonUtils.distance(coordinates[index - 1][0], coordinates[index - 1][1], coordinates[index][0], coordinates[index][1])
            
            index += 1

        return result

    @staticmethod
    def distance(x1, y1, x2, y2):
        R = 6371000
        dx = (x2 - x1) * pi / 180
        y1 = y1 * pi / 180
        y2 = y2 * pi / 180
        x = dx * cos((y1+y2)/2)
        y = (y2-y1)
        d = sqrt(x*x + y*y)
        return R * d

class StatisticTransformer:
    @staticmethod
    def transform_pekerjaan_raw(penduduks):
        result = []
        for source in sources["pekerjaan"]:
            total_male = 0
            total_female = 0

            for penduduk in penduduks:
                if penduduk is None or penduduk.pekerjaan is None:
                    continue

                if source.lower() in penduduk.pekerjaan.lower() and penduduk.jenis_kelamin == "Laki-Laki":
                    total_male += 1
                elif source.lower() in penduduk.pekerjaan.lower() and penduduk.jenis_kelamin == "Perempuan":
                    total_female += 1
              
            result.append({"jenis_kelamin": "Laki-Laki", "jumlah": total_male, "pekerjaan": source })
            result.append({"jenis_kelamin": "Perempuan", "jumlah": total_female, "pekerjaan": source })
            
        return result

    @staticmethod
    def transform_pendidikan_raw(penduduks):
        result = []
        for key in pendidikan_groups.iterkeys():
            total_male = 0
            total_female = 0
            group = pendidikan_groups[key]

            for penduduk in penduduks:
                if penduduk is None or penduduk.pendidikan is None:
                    continue
                
                pendidikan = penduduk.pendidikan

                if pendidikan in group and penduduk.jenis_kelamin == "Laki-Laki":
                    total_male += 1
                elif pendidikan in group and penduduk.jenis_kelamin == "Perempuan":
                    total_female += 1
                
            result.append({"jenis_kelamin": "Laki-Laki", "jumlah": total_male, "pendidikan": key })
            result.append({"jenis_kelamin": "Perempuan", "jumlah": total_female, "pendidikan": key })
            
        return result

    @staticmethod
    def transform_penduduk_productivity_raw(penduduks): 
       result = []
       today = date.today()
       
       for key in penduduk_range.iterkeys():
           bounds = penduduk_range[key]
           range = StatisticTransformer.create_range(bounds[0], bounds[1])
           total_male = 0
           total_female = 0
           total_unknown = 0

           for penduduk in penduduks:
              print(penduduk.nama_penduduk)
              print(penduduk.tanggal_lahir)

              if penduduk.tanggal_lahir is None:
                  continue

              age = today.year - penduduk.tanggal_lahir.year
            
              if age in range:
                  if penduduk.jenis_kelamin == "Laki-Laki":
                     total_male += 1
                  elif penduduk.jenis_kelamin == "Perempuan":
                     total_female += 1
                  else:
                     total_unknown += 1

           result.append({"jenis_kelamin": "Laki-Laki", "jumlah": total_male, "key": key })
           result.append({"jenis_kelamin": "Perempuan", "jumlah": total_female, "key": key})
           result.append({"jenis_kelamin": "Tidak Diketahui", "jumlah": total_unknown, "key": key })

       return result

    @staticmethod
    def create_range(lower, upper):
        result = []
        for i in range(lower, upper):
            result.append(i)

        return result

class LayoutTransformer:
    @staticmethod
    def transform(layout, geoJsons, penduduks):
        pekerjaan_statistic_raw = StatisticTransformer.transform_pekerjaan_raw(penduduks)
        pendidikan_statistic_raw = StatisticTransformer.transform_pendidikan_raw(penduduks)
        penduduk_statistic_raw = StatisticTransformer.transform_penduduk_productivity_raw(penduduks)

        apbdes_features = filter(lambda x: x.type == 'log_pembangunan', geoJsons)
        landuse_features = filter(lambda x: x.type == 'landuse', geoJsons)
        boundary_features = filter(lambda x: x.type == 'boundary', geoJsons)
        highway_features = filter(lambda x: x.type == 'network_transportation', geoJsons)
        building_features = filter(lambda x: x.type == 'facilities_infrastructures', geoJsons)

        layout.data = {"base": [], "apbdes": [], "landuses": [], "boundaries": [], "highways": [], "schools": [], "houses": [], "properties": {}}

        if len(apbdes_features) > 0:
            layout.data["apbdes"] = apbdes_features[0].data["features"]

        if len(landuse_features) > 0:
            layout.data["landuses"] = landuse_features[0].data["features"]

        if len(boundary_features) > 0:
            layout.data["boundaries"] = boundary_features[0].data["features"]

        for feature in layout.data["boundaries"]:
            layout.data["base"].append(feature)

        if len(highway_features) > 0:
            layout.data["highways"] = highway_features[0].data["features"]

        for feature in layout.data["highways"]:
            layout.data["base"].append(feature)

        if len(building_features) > 0:
            for feature in building_features[0].data["features"]:

                if feature["geometry"]["type"] == "Polygon":
                    layout.data["base"].append(feature)

                if feature.has_key("properties"):
                    if feature["properties"].has_key("amenity"):
                        if feature["properties"]["amenity"] == "school":
                            layout.data["schools"].append(feature)
                    if feature["properties"].has_key("building"):
                        if feature["properties"]["building"] == "house":
                            layout.data["houses"].append(feature)

        
        layout.data["properties"] = {"statistics": []}
        layout.data["properties"]["statistics"] = {"pekerjaan": pekerjaan_statistic_raw, "pendidikan": pendidikan_statistic_raw, "penduduk": penduduk_statistic_raw}
        return layout 


