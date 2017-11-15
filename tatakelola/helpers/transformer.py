import logging
import simplejson as json
import geojson
from tatakelola.models import Summary, PendudukReference

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


class SummaryTransformer:
    @staticmethod
    def transform(penduduks):
        summary = Summary()
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

        ref = PendudukReference()
        for penduduk in penduduks:
            if penduduk.jenis_kelamin == 'Laki-laki':
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
