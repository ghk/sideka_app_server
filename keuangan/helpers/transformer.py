import simplejson as json
import numbers
from keuangan.models import SpendingRecapitulation, ProgressTimeline, ProgressRecapitulation


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


class ProgressTimelineTransformer:
    @staticmethod
    def transform(penerimaan_rincis, spp_rincis, year, region):
        result = []
        max_month = 1
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        data = {}

        for month in months:
            pt = ProgressTimeline()
            pt.year = year
            pt.month = month
            pt.fk_region_id = region.id
            pt.transferred_dds = 0
            pt.transferred_add = 0
            pt.transferred_pbh = 0
            pt.realized_spending = 0
            data[month] = pt

        for rinci in penerimaan_rincis:
            month = rinci.penerimaan.tanggal.month
            if (max_month < month):
                max_month = month

            for mon in range(month, 13, 1):
                sumber_dana = str(rinci.sumber_dana).strip()
                if sumber_dana == 'DDS':
                    data[mon].transferred_dds += rinci.nilai
                elif sumber_dana == 'ADD':
                    data[mon].transferred_add += rinci.nilai
                elif sumber_dana == 'PBH':
                    data[mon].transferred_pbh += rinci.nilai

        for rinci in spp_rincis:
            month = rinci.spp.tanggal.month
            if (max_month < month):
                max_month = month

            for mon in range(month, 13, 1):
                data[mon].realized_spending += rinci.nilai

        for key, datum in data.iteritems():
            if (key <= max_month):
                result.append(datum)

        return result


class ProgressRecapitulationTransformer:
    @staticmethod
    def transform(anggarans, penerimaan_rincis, spp_rincis, year, region):
        pr = ProgressRecapitulation()
        pr.year = year
        pr.fk_region_id = region.id
        pr.budgeted_revenue = 0
        pr.transferred_revenue = 0
        pr.realized_spending = 0

        budgeted_revenue = 0
        budgeted_revenue_pak = 0

        for rinci in penerimaan_rincis:
            sumber_dana = str(rinci.sumber_dana).strip()
            if sumber_dana == 'DDS' or sumber_dana == 'ADD' or sumber_dana == 'PBH':
                pr.transferred_revenue += rinci.nilai

        for rinci in spp_rincis:
            pr.realized_spending += rinci.nilai

        for anggaran in anggarans:
            if (anggaran.kode_rekening.startswith('4.')):
                if (anggaran.jumlah_satuan is not None and anggaran.harga_satuan is not None):
                    budgeted_revenue += anggaran.jumlah_satuan * anggaran.harga_satuan
                if (anggaran.jumlah_satuan_pak is not None and anggaran.harga_satuan_pak is not None):
                    budgeted_revenue_pak += anggaran.jumlah_satuan_pak * anggaran.harga_satuan_pak

        if budgeted_revenue_pak > 0:
            pr.budgeted_revenue = budgeted_revenue_pak
        else:
            pr.budgeted_revenue = budgeted_revenue

        return pr


class SiskeudesPenganggaranTransformer:
    @staticmethod
    def transform(anggarans):
        for anggaran in anggarans:
            anggaran.kode_rekening = anggaran.kode_rekening.rstrip('.')
            anggaran.kode_kegiatan = anggaran.kode_kegiatan.rstrip('.')

            if (anggaran.jumlah_satuan is not None and anggaran.harga_satuan is not None):
                anggaran.anggaran = anggaran.jumlah_satuan * anggaran.harga_satuan
            if (anggaran.jumlah_satuan_pak is not None and anggaran.harga_satuan_pak is not None):
                anggaran.anggaran_pak = anggaran.jumlah_satuan_pak * anggaran.harga_satuan_pak
            if (isinstance(anggaran.anggaran_pak, numbers.Number)):
                anggaran.perubahan = anggaran.anggaran_pak - anggaran.anggaran

        for anggaran in anggarans:
            if anggaran.satuan:
                SiskeudesPenganggaranTransformer.recursive_sum(anggarans, anggaran.kode_rekening,
                                                               anggaran.kode_kegiatan, anggaran.row_number,
                                                               anggaran.anggaran, anggaran.anggaran_pak)

        return anggarans

    @staticmethod
    def recursive_sum(anggarans, kode_rekening, kode_kegiatan, row_number, value, value_pak):
        new_kode_rekening = '.'.join(kode_rekening.split('.')[:-1])
        new_kode_kegiatan = '.'.join(kode_kegiatan.split('.')[:-1])
        if not new_kode_rekening:
            return

        filtered_rekening_anggarans = [anggaran for anggaran in anggarans if
                                       anggaran.kode_rekening == new_kode_rekening]
        filtered_kegiatan_anggarans = [anggaran for anggaran in anggarans if
                                       anggaran.kode_kegiatan and anggaran.kode_kegiatan == kode_kegiatan]
        entity = SiskeudesPenganggaranTransformer.find_nearest(filtered_rekening_anggarans, row_number, False)
        kegiatan_entity = SiskeudesPenganggaranTransformer.find_nearest(filtered_kegiatan_anggarans, row_number, True)

        if (entity is not None):
            if (value is not None):
                if (entity.anggaran is None or not entity.anggaran):
                    entity.anggaran = 0
                entity.anggaran += value

            if (value_pak is not None):
                if (entity.anggaran_pak is None or not entity.anggaran_pak):
                    entity.anggaran_pak = 0
                entity.anggaran_pak += value

        if (kegiatan_entity is not None):
            if (value is not None):
                if (kegiatan_entity.anggaran is None or not kegiatan_entity.anggaran):
                    kegiatan_entity.anggaran = 0
                kegiatan_entity.anggaran += value

            if (value_pak is not None):
                if (kegiatan_entity.anggaran_pak is None or not kegiatan_entity.anggaran_pak):
                    kegiatan_entity.anggaran_pak = 0
                kegiatan_entity.anggaran_pak += value

        SiskeudesPenganggaranTransformer.recursive_sum(anggarans, new_kode_rekening, new_kode_kegiatan, row_number,
                                                       value, value_pak)

    @staticmethod
    def find_nearest(anggarans, row_number, is_kegiatan):
        if len(anggarans) == 0:
            return None

        current = anggarans[0]
        for anggaran in anggarans:
            if (is_kegiatan and
                    not anggaran.kode_rekening and
                        anggaran.row_number < row_number and
                        anggaran.row_number > current.row_number):
                current = anggaran
            if (not is_kegiatan and anggaran.row_number < row_number and anggaran.row_number > current.row_number):
                current = anggaran
        return current
