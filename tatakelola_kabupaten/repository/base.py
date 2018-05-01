from common.helpers import QueryHelper


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

    def add_all(self, entities):
        for entity in entities:
            self.db.session.add(entity)

    def bulk_add_all(self, entities):
        self.db.session.bulk_save_objects(entities)

    def delete_all(self):
        self.db.session.query(self.model) \
            .delete()
