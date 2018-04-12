import simplejson as json
import pandas
import numpy
from keuangan import db
from scipy.spatial.distance import pdist, squareform
from keuangan.models import BudgetRecapitulation, ProgressTimeline, ProgressRecapitulation, BudgetLikelihood

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


class BudgetRecapitulationTransformer:
    @staticmethod
    def transform(anggarans, year, region, budget_types):
        result = []

        for budget_type in budget_types:
            sr = BudgetRecapitulation()
            sr.fk_type_id = budget_type.id
            sr.fk_region_id = region.id
            sr.year = year

            budgeted = 0
            budgeted_pak = 0

            for anggaran in anggarans:
                if budget_type.is_revenue:
                    if anggaran.sumber_dana != budget_type.code:
                        continue
                    if not anggaran.kode_rekening.startswith('4.'):
                        continue
                elif not budget_type.is_revenue and not (
                        anggaran.kode_kegiatan.startswith(region.siskeudes_code + '.' + budget_type.code)):
                    continue

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
            if rinci.penerimaan.tanggal is None:
                continue

            month = rinci.penerimaan.tanggal.month
            if (max_month < month):
                max_month = month

            for mon in range(month, 13, 1):
                if rinci.nilai is None:
                    rinci.nilai = 0
                sumber_dana = str(rinci.sumber_dana).strip()
                if sumber_dana == 'DDS':
                    data[mon].transferred_dds += rinci.nilai
                elif sumber_dana == 'ADD':
                    data[mon].transferred_add += rinci.nilai
                elif sumber_dana == 'PBH':
                    data[mon].transferred_pbh += rinci.nilai

        for rinci in spp_rincis:
            if rinci.spp.tanggal  is None:
                continue

            month = rinci.spp.tanggal.month
            if (max_month < month):
                max_month = month

            for mon in range(month, 13, 1):
                if rinci.nilai is None:
                    rinci.nilai = 0
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
                if rinci.nilai is not None:
                    pr.transferred_revenue += rinci.nilai

        for rinci in spp_rincis:
            if rinci.nilai is not None:
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

        filtered_anggarans = []

        for anggaran in anggarans:
            anggaran.kode_rekening = anggaran.kode_rekening.rstrip('.')
            anggaran.kode_kegiatan = anggaran.kode_kegiatan.rstrip('.')

            if (anggaran.jumlah_satuan is not None and anggaran.harga_satuan is not None):
                anggaran.anggaran = anggaran.jumlah_satuan * anggaran.harga_satuan
            if (anggaran.jumlah_satuan_pak is not None and anggaran.harga_satuan_pak is not None):
                anggaran.anggaran_pak = anggaran.jumlah_satuan_pak * anggaran.harga_satuan_pak
                anggaran.perubahan = anggaran.anggaran_pak - anggaran.anggaran

            # This code is checking if bidang and kegiatan are already filled from sideka
            if (anggaran.satuan is None and anggaran.anggaran is None):
                filtered_anggarans.append(anggaran)

        for anggaran in anggarans:
            if anggaran.satuan:
                # Using filtered_anggarans improves speed by 40%
                SiskeudesPenganggaranTransformer.recursive_sum(filtered_anggarans, anggaran.kode_rekening,
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
                entity.anggaran_pak += value_pak

        if (kegiatan_entity is not None):
            if (value is not None):
                if (kegiatan_entity.anggaran is None or not kegiatan_entity.anggaran):
                    kegiatan_entity.anggaran = 0
                kegiatan_entity.anggaran += value

            if (value_pak is not None):
                if (kegiatan_entity.anggaran_pak is None or not kegiatan_entity.anggaran_pak):
                    kegiatan_entity.anggaran_pak = 0
                kegiatan_entity.anggaran_pak += value_pak

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


stop_words = ['/', '&', 'dan', 'atau', ',', '.', 'desa', 'desa/data', 'hanura', 'kegiatan', 'di', 'ke', '...', ';',
              'petaaset', 'dalam', 'pakraman']
mapping = ["bpd", "badan permusyawaratan", "kantor"]
class SiskeudesLikelihoodTransformer:

    @staticmethod
    def create_documents():
        docs = pandas.read_sql("select distinct(uraian) from view_learn_kegiatan order by uraian asc", db.session.connection())
        docs['uraian'].fillna(0, inplace=True)
        return docs['uraian']

    @staticmethod
    def tokenize(doc):
        tokens = []
        words = doc.strip().lower().split()
        for word in words:
            if word in stop_words:
                continue
            tokens.append(word.strip())

        return tokens
    @staticmethod
    def process(text, documents):
        token = SiskeudesLikelihoodTransformer.tokenize(text)
        max = -1000
        result = None

        for d, doc in enumerate(documents):
            if text.strip().lower() == doc.strip().lower():
                continue

            token_doc = SiskeudesLikelihoodTransformer.tokenize(doc)
            score = SiskeudesLikelihoodTransformer.calculate_scores(token, token_doc)

            if score > 25:
                if score > max:
                    if len(''.join(token)) > len(''.join(token_doc)):
                        result = {'original': text, 'normalized': ' '.join(token_doc), 'score': score}
                    else:
                        result = {'original': text, 'normalized': ' '.join(token), 'score': score}
                    max = score
        if result is None:
            return {'original': text, 'normalized': ' '.join(token), 'score': 0}
        return result

    @staticmethod
    def calculate_scores(d1, d2):
        lindex = 0
        uindex = 0
        if len(d1) > len(d2):
            lindex = d2
            uindex = d1
        else:
            lindex = d1
            uindex = d2

        score = 0
        for i, t in enumerate(lindex):
            if i == 0:
                if lindex[i] == uindex[i]:
                    score += 30
                else:
                    score -= 30
            elif i == len(lindex) - 1:
                if lindex[i] == uindex[i]:
                    score += 30
                else:
                    score -= 30
            else:
                if lindex[i] == uindex[i]:
                    score += 20
            if d1[i] in mapping or d2[i] in mapping:
                score += 30
        if score == 0:
            return score
        return score / len(lindex)

    @staticmethod
    def normalize():
        documents = SiskeudesLikelihoodTransformer.create_documents()
        docs = pandas.read_sql("select fk_region_id, uraian, percentage from view_learn_kegiatan order by fk_region_id", db.session.connection())
        docs['uraian'].fillna(0, inplace=True)
        d = []
        for idx, doc in enumerate(docs['uraian']):
            result = SiskeudesLikelihoodTransformer.process(doc, documents)
            d.append(result['normalized'])
        docs['normalized_uraian'] = d
        docs = pandas.DataFrame(docs)
        return docs

    @staticmethod
    def transform(view_learn_kegiatan_query, year):
        d = SiskeudesLikelihoodTransformer.normalize()
        # Filter Data
        df = d[d.percentage >= 0.005]
        df = df.reset_index(drop=True)
        data = pandas.pivot_table(df, index=["fk_region_id"], values=["percentage"], columns=["normalized_uraian"])

        # Fill missing data
        data = data.fillna(0)

        # Build matrix pdist
        distances = pdist(data.values, metric='euclidean')
        distances_matrix = squareform(distances)

        table = pandas.DataFrame(distances_matrix)
        table['fk_regions'] = data.index.tolist()
        table = table[['fk_regions'] + table.columns[:-1].tolist()]

        # Prepare for result matrix
        fk_regions = numpy.array(table['fk_regions'])
        distances = numpy.array(table)

        # Transform Matrix
        rank_desas = []
        for idx_1, dis_1 in enumerate(distances):
            for idx_2, dis_2 in enumerate(dis_1):
                region_distances = [dis_1[0]]
                if idx_1 == idx_2:
                    continue
                ref_fk_region = fk_regions[idx_2 - 1]
                region_distances.append(ref_fk_region)
                region_distances.append(dis_2)
                # print region_distances
                rank_desas.append(region_distances)

        rank_table = pandas.DataFrame(rank_desas)
        rank_table.columns = ["id_desa", "id_likelihood", "euclidean_distances"]

        # Sort result
        rank_desas = sorted(rank_desas, key=lambda x: (x[0], x[2]))
        split = lambda rank_desas, n=len(data): [rank_desas[i:i + n] for i in range(0, len(rank_desas), n)]
        rank_desas_splitted = split(rank_desas)

        likelihood_table = []

        for desa in rank_desas_splitted:
            desa = [x for x in desa if x[2] != 0]
            likelihood_table.append(desa[0:5])

        zipped = numpy.concatenate(likelihood_table)
        likelihood_table = pandas.DataFrame(zipped)
        likelihood_table.columns = ["fk_region_id", "fk_region_likelihood_id", "euclidean_score"]

        # Add column rank
        rank = [1, 2, 3, 4, 5]

        # Join column rank into dataframe
        likelihood_table = likelihood_table.join(
            pandas.DataFrame(rank * (len(likelihood_table) / len(rank) + 1), columns=['rank']))

        result = []
        for likelihood in likelihood_table.iterrows():
            sl = BudgetLikelihood()
            sl.year = year
            sl.euclidean_score = likelihood[1]['euclidean_score']
            sl.rank = likelihood[1]['rank']
            sl.fk_region_id = likelihood[1]['fk_region_id']
            sl.fk_region_likelihood_id = likelihood[1]['fk_region_likelihood_id']
            result.append(sl)

        return result
