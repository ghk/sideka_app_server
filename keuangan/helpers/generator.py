from keuangan.models import ProgressRecapitulation
from keuangan.models import ProgressTimeline
from keuangan.models import ProgressRevenue
from keuangan.models import ProgressRealization
from keuangan.models import SpendingRecapitulation

from datetime import datetime
import random
import decimal


class Generator:
    @staticmethod
    def generate_progress_recapitulation():
        result = ProgressRecapitulation()
        result.apbn_key = '2017'
        result.budgeted_revenue = decimal.Decimal(random.randrange(100000000000, 150000000000)) / 100
        result.transferred_revenue = decimal.Decimal(random.randrange(50000000000, 100000000000)) / 100
        result.realized_spending = decimal.Decimal(random.randrange(25000000000, 50000000000)) / 100
        result.date_created = datetime.utcnow()
        result.date_modified = datetime.utcnow()
        return result


    @staticmethod
    def generate_progress_timeline():
        result = ProgressTimeline()
        result.apbn_key = '2017'
        result.transferred_dd = decimal.Decimal(random.randrange(5000000000, 10000000000)) / 100
        result.transferred_add = decimal.Decimal(random.randrange(5000000000, 10000000000)) / 100
        result.transferred_bhpr = decimal.Decimal(random.randrange(5000000000, 10000000000)) / 100
        result.realized_spending = decimal.Decimal(random.randrange(5000000000, 10000000000)) / 100
        return result


    @staticmethod
    def generate_spending_recapitulations():
        result = SpendingRecapitulation()
        result.budgeted = decimal.Decimal(random.randrange(10000000000, 100000000000)) / 100
        result.realized = result.budgeted / (random.randrange(1, 10))
        return result


    @staticmethod
    def generate_progress_revenue():
        result = ProgressRevenue()
        result.year = '2017'
        result.code = '0001/TBP/19.09/2017'
        result.description = 'Penerimaan Transfer Alokasi Dana Desa'
        result.value = decimal.Decimal(15600000)
        result.type = 'ADD'
        result.date = datetime.now()
        result.source_name = 'BPKAD'
        result.source_address = 'Singaparna - Tasikmalaya'
        result.source_signature = 'BKAD'
        result.account_number = '0005465001100'
        result.bank_name = 'BJB'
        return result;


    @staticmethod
    def generate_progress_realization():
        result = ProgressRealization()
        result.year = '2017'
        result.code = '0001/SPP/19.09/2017'
        result.description = 'Pembayaran SILTAP Kepala Desa Dan Perangkat'
        result.value = decimal.Decimal(15600000)
        result.type = 'Definitif'
        result.date = datetime.now()
        return result



