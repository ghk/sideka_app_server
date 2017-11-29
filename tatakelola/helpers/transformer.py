import logging
import simplejson as json
import geojson
import math

from tatakelola.models import Summary, PendudukReference
from area import area

logger = logging.getLogger('tatakelola')

class ContentTransformer:
    @staticmethod
    def transform(content):
        serialized_content = json.loads(content)
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
        serialized_content = json.loads(content)
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
        summary.penduduk_job_lain = 0
        summary.penduduk_total_kk = 0

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
        features = data['features'];

        return ParsePemetaanData.parse(features, type, summary)

class ParsePemetaanData:
    @staticmethod
    def parse(features, type, summary):
        pipe_count = 0
        farmland_trees = []
        orchard_orchards = []
        forest_trees = []

        for feature in features:
            if feature.has_key('properties') == False:
                continue

            properties = feature['properties']

            if type == 'boundary':
                if feature['geometry']['type'] != 'Polygon':
                    continue
                if feature['properties'].has_key('admin_level') == False:
                    continue
                if feature['properties']['admin_level'] != 7:
                    continue
                summary.pemetaan_desa_boundary += area(feature['geometry'])
            elif type == 'landuse':
                if properties.has_key('landuse') == False:
                    continue
                if properties['landuse'] == 'farmland':
                    summary.pemetaan_potential_farmland += 1
                    if properties.has_key('farmland'):
                        farmland_trees.append(properties['farmland'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_potential_farmland_area += area(feature['geometry'])
                elif properties['landuse'] == 'orchard':
                    summary.pemetaan_potential_orchard += 1
                    if properties.has_key('forest'):
                        orchard_orchards.append(properties['forest'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_potential_orchard_area += area(feature['geometry'])
                elif properties['landuse'] == 'forest':
                    summary.pemetaan_potential_forest += 1
                    if properties.has_key('forest'):
                        forest_trees.append(properties['forest'].lower().strip())
                    if feature['geometry']['type'] == 'Polygon':
                        summary.pemetaan_potential_forest_area += area(feature['geometry'])
            elif type == 'waters':
                if properties.has_key('natural'):
                    if properties['natural'] == 'spring':
                        summary.pemetaan_water_natural += 1
                        if feature['geometry']['type'] == 'Polygon':
                            summary.pemetaan_water_natural_area += area(feature['geometry'])
                elif properties.has_key('waterway'):
                    if properties['waterway'] == 'pipe_system':
                        summary.pemetaan_water_pipe += 1
                        pipe_count += 1

                        if math.isnan(properties['width']) == False:
                            summary.pemetaan_water_pipe += int(properties['width'])
            elif type == 'electricity':
                if properties.has_key('electricity_watt'):
                    if math.isnan(properties['electricity_watt']) == False:
                        if int(properties['electricity_watt']) > 0:
                            summary.pemetaan_electricity_house += 1
            elif type == 'school':
                if properties.has_key('amenity') == False:
                    continue
                if properties['amenity'] != 'school':
                    continue
                if properties.has_key('isced') == False:
                    continue

                if properties['isced'] == 0:
                    summary.pemetaan_school_tk += 1
                elif properties['isced'] == 1:
                    summary.pemetaan_school_sd += 1
                elif properties['isced'] == 2:
                    summary.pemetaan_school_smp += 1
                elif properties['isced'] == 3:
                    summary.pemetaan_school_sma += 1
                elif properties['isced'] == 4:
                    summary.pemetaan_school_pt += 1

        if pipe_count > 0:
            summary.pemetaan_water_pipe_width_avg = summary.pemetaan_water_pipe_width_avg / pipe_count

        summary.pemetaan_potential_farmland_trees = ','.join(map(str, farmland_trees))
        summary.pemetaan_potential_orchard_orchards = ','.join(map(str, orchard_orchards))
        summary.pemetaan_potential_forest_trees = ','.join(map(str, forest_trees))

        return summary