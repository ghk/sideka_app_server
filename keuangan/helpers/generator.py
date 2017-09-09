from keuangan.models import ProgressRecapitulation
from keuangan.models import ProgressTimeline
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
    def generate_spending_recapitulations(is_realization):
        result = SpendingRecapitulation()
        result.value = decimal.Decimal(random.randrange(10000000000, 100000000000)) / 100
        if is_realization:
            result.value = result.value / (random.randrange(1, 10))
        return result