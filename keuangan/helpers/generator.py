from keuangan.models import ProgressRecapitulation
from keuangan.models import ProgressTimeline
from datetime import datetime
import random
import decimal


class Generator:
    @staticmethod
    def generate_progress_recapitulation(self):
        result = ProgressRecapitulation()
        result.apbn_key = '2017'
        result.realized_revenue = decimal.Decimal(random.randrange(50000000000, 100000000000) / 100)
        result.transferred_revenue = decimal.Decimal(random.randrange(100000000000, 150000000000) / 100)
        result.date_created = datetime.utcnow()
        result.date_modified = datetime.utcnow()
        return result

    @staticmethod
    def generate_progress_timeline(self):
        result = ProgressTimeline()
        result.apbn_key = '2017'
        result.transferred_dd = decimal.Decimal(random.randrange(50000000000, 100000000000) / 100)
        result.transferred_add = decimal.Decimal(random.randrange(50000000000, 100000000000) / 100)
        result.transferred_bhpr = decimal.Decimal(random.randrange(50000000000, 100000000000) / 100)
        result.realized_spending = decimal.Decimal(random.randrange(50000000000, 100000000000) / 100)
        return result
