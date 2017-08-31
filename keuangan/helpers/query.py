from sqlalchemy import asc, desc

class QueryHelper:

    @staticmethod
    def page(query, page, per_page):
        if page <= 0:
            raise AttributeError('page needs to be >= 1')
        if per_page <= 0:
            raise AttributeError('per_page needs to be >= 1')
        return query.limit(per_page).offset((page - 1) * per_page)

    @staticmethod
    def sort(query, model, *args):
        for column in args:
            if column.startswith('-'):
                attr = getattr(model, column[1:])
                query = query.order_by(desc(attr))
            else:
                attr = getattr(model, column)
                query = query.order_by(asc(attr))
        return query

    @staticmethod
    def build_page_query(query, request):
        page = request.args.get('page')
        per_page = request.args.get('per_page')
        if (page is not None and per_page is not None):
            return QueryHelper.page(query, int(page), int(per_page))
        else:
            return query

    @staticmethod
    def build_sort_query(query, model, request):
        sort = request.args.get('sort')
        if (sort is not None):
            sort = str(sort)
            sort_arr = sort.split(',')
            return QueryHelper.sort(query, model, *sort_arr)
        else:
            return query
