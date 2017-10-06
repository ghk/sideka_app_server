import simplejson as json
from keuangan.models import SpendingRecapitulation

class ContentTransformer:

    @staticmethod
    def transform(content):
        serialized_content = json.loads(content)
        columns = {}
        result = {}

        for column in serialized_content['columns'].keys():
            columns[column] = serialized_content['columns'][column]
            result[column] = []
            for data in serialized_content['data'][column]:
                obj = dict.fromkeys(columns[column])
                for index, datum in enumerate(data):
                    obj[columns[column][index]] = datum
                result[column].append(obj)

        return result


class SpendingRecapitulationTransformer:

    @staticmethod
    def transform(anggarans, year, region, spending_types):
        result = []

        for spending_type in spending_types:
            sr = SpendingRecapitulation()
            sr.fk_type_id = spending_type.id
            sr.fk_region_id = region.id
            sr.year = year

            budgeted = 0
            budgeted_pak = 0

            for anggaran in anggarans:
                if not anggaran.kode_kegiatan.startswith(region.siskeudes_code + '.' + spending_type.code):
                    continue;
                if anggaran.jumlah_satuan is not None and anggaran.harga_satuan is not None:
                    budgeted += anggaran.jumlah_satuan * anggaran.harga_satuan
                if anggaran.jumlah_satuan_pak is not None and anggaran.harga_satuan_pak is not None:
                    budgeted_pak += anggaran.jumlah_satuan_pak * anggaran.harga_satuan_pak

            if budgeted_pak != 0:
                sr.budgeted = budgeted_pak
            else:
                sr.budgeted = budgeted

            result.append(sr)

        return result
