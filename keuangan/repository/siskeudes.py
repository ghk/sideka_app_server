from time import time

class SiskeudesRepository():
    def get(self, pid):
        return self.db.session.query(self.model) \
            .filter(self.model.pid == pid) \
            .first()

    def get_by_region(self, region_id):
        return self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()
        self.db.session.commit()

    def add_all(self, contents, region, year):
        #t0 = time()
        i = 1;
        for content in contents:
            content.row_number = i
            content.year = year
            content.fk_region_id = region.id
            i += 1
            self.db.session.add(content)
        self.db.session.commit()
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
        self.db.session.commit()
        #print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')

