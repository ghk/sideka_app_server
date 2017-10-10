from keuangan.helpers import QueryHelper

class SiskeudesRepository():
    def get(self, pid):
        return self.db.session.query(self.model) \
            .filter(self.model.pid == pid) \
            .first()

    def get_by_region(self, region_id, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.fk_region_id == region_id).all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()

    def add_all(self, contents, region, year):
        #t0 = time()
        i = 1;
        for content in contents:
            content.row_number = i
            content.year = year
            content.fk_region_id = region.id
            i += 1
            self.db.session.add(content)
        #print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')

    def bulk_add_all(self, contents, region, year):
        #t0 = time()
        i = 1;
        for content in contents:
            content.row_number = i
            content.year = year
            content.fk_region_id = region.id
            i += 1

        self.db.session.bulk_save_objects(contents)
        #print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')

