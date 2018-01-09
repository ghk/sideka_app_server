from keuangan.helpers import QueryHelper


class BaseRepository:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def get(self, id):
        return self.db.session.query(self.model) \
            .filter(self.model.id == id) \
            .first()

    def all(self, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()

    def count(self):
        return self.db.session.query(self.model).count()

    def add(self, entity):
        self.db.session.add(entity)

    def delete_all(self):
        self.db.session.query(self.model) \
            .delete()


class BaseRegionRepository:
    def all_by_year(self, year, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.year == year).all()

    def count_by_year(self, year):
        return self.db.session.query(self.model).filter(self.model.year == year).count()

    def get_by_region(self, region_id, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.fk_region_id == region_id).all()

    def get_by_region_and_year(self, region_id, year, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query \
            .filter(self.model.fk_region_id == region_id) \
            .filter(self.model.year == year) \
            .all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()

    def delete_by_year(self, year):
        self.db.session.query(self.model) \
            .filter(self.model.year == year) \
            .delete()

    def delete_by_region_and_year(self, region_id, year):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .filter(self.model.year == year) \
            .delete()


class BaseSiskeudesRepository:
    def get(self, pid):
        return self.db.session.query(self.model) \
            .filter(self.model.pid == pid) \
            .first()

    def add_all(self, contents, region, year):
        # t0 = time()
        i = 1;
        for content in contents:
            content.row_number = i
            content.year = year
            content.fk_region_id = region.id
            i += 1
            self.db.session.add(content)
            # print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')

    def bulk_add_all(self, contents, region, year):
        # t0 = time()
        i = 1;
        for content in contents:
            content.row_number = i
            content.year = year
            content.fk_region_id = region.id
            i += 1

        self.db.session.bulk_save_objects(contents)
        # print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')
