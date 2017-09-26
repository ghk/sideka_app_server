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
        self.db.session.commit()

    def delete_all(self):
        self.db.session.query(self.model) \
            .delete()
        self.db.session.commit()