import operator

from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import SdPostScores, SdPostScoresSchema
from tatakelola.repository import PostRepository, SidekaDesaRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('post', __name__)
post_repository = PostRepository(db)
sideka_desa_repository = SidekaDesaRepository(db)

@app.route('/post/<string:code>', methods=['GET'])
def get_by_desa_code(code):
    data = []
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    desas = sideka_desa_repository.get_by_code(code)
   
    for desa in desas:
        posts = post_repository.get_by_desa_id(desa.blog_id, page_sort_params=page_sort_params)

        if len(posts) > 0:
            result = SdPostScoresSchema(many=True).dump(posts)
            data.append(result.data)
    
    return jsonify(data)