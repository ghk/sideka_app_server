from sqlalchemy import asc, desc
from sqlalchemy.orm import RelationshipProperty

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
            attrs = column.split('.')
            if attrs[0].startswith('-'):
                func = desc
                attr = getattr(model, attrs[0][1:])
            else:
                func = asc
                attr = getattr(model, attrs[0])

            if len(attrs) == 1:
                query = query.order_by(func(attr))
            else:
                sub_model = attr.property.mapper.class_
                sub_attr = getattr(sub_model, attrs[1])
                query = query.join(sub_model)
                query = query.order_by(func(sub_attr))
        return query


    @staticmethod
    def build_page_query(query, page, per_page):
        if (page is not None and per_page is not None):
            return QueryHelper.page(query, int(page), int(per_page))
        else:
            return query


    @staticmethod
    def build_sort_query(query, model, sort):
        if (sort is not None):
            sort = str(sort)
            sort_arr = sort.split(',')
            return QueryHelper.sort(query, model, *sort_arr)
        else:
            return query


    @staticmethod
    def build_page_sort_query(query, model, page_sort_params):
        if (page_sort_params is not None):
            query = QueryHelper.build_sort_query(query, model, page_sort_params['sort'])
            query = QueryHelper.build_page_query(query, page_sort_params['page'], page_sort_params['per_page'])
        return query


    @staticmethod
    def get_page_sort_params_from_request(request):
        page = request.args.get('page')
        per_page = request.args.get('per_page')
        sort = request.args.get('sort')
        result = {
            'page': page,
            'per_page': per_page,
            'sort': sort
        }
        return result