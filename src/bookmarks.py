from flask import Blueprint, jsonify, request
import validators
from src.const.http_status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_409_CONFLICT, \
    HTTP_404_NOT_FOUND
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from

bookmarks = Blueprint('bookmarks', __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['GET', 'POST'])
@jwt_required()
def bookmark():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'URL is not valid.'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL is already existed.'
            }), HTTP_409_CONFLICT

        bookmark_item = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark_item)
        db.session.commit()

        return jsonify({
            'message': 'Created bookmark successfully!',
            'Bookmark info': {
                'id': bookmark_item.id,
                'url': bookmark_item.url,
                'short_url': bookmark_item.short_url,
                'visit': bookmark_item.visits,
                'body': bookmark_item.body,
                'created_at': bookmark_item.create_at,
                'update_at': bookmark_item.update_at
            }
        }), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 2, type=int)

        bookmark_list = Bookmark.query.filter_by(user_id=current_user). \
            paginate(page=page, per_page=per_page)
        data = []
        for bookmark_item in bookmark_list.items:
            data.append({
                'id': bookmark_item.id,
                'url': bookmark_item.url,
                'short_url': bookmark_item.short_url,
                'visit': bookmark_item.visits,
                'body': bookmark_item.body,
                'created_at': bookmark_item.create_at,
                'update_at': bookmark_item.update_at
            })
        meta = {
            'page': bookmark_list.page,
            'pages': bookmark_list.pages,
            'total_count': bookmark_list.total,
            'prev_page': bookmark_list.prev_num,
            'next_page': bookmark_list.next_num,
            'has_next': bookmark_list.has_next,
            'has_prev': bookmark_list.has_prev
        }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK


@bookmarks.route('/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark_item = Bookmark.query.filter_by(user_id=current_user, id=id)\
        .first()

    if not bookmark_item:
        return jsonify({'message': 'Item not found.'}), HTTP_404_NOT_FOUND

    data = {
                'id': bookmark_item.id,
                'url': bookmark_item.url,
                'short_url': bookmark_item.short_url,
                'visit': bookmark_item.visits,
                'body': bookmark_item.body,
                'created_at': bookmark_item.create_at,
                'update_at': bookmark_item.update_at
            }

    match request.method:
        case 'GET':
            return jsonify(data), HTTP_200_OK
        case 'DELETE':
            bid = bookmark_item.id
            url = bookmark_item.url

            db.session.delete(bookmark_item)
            db.session.commit()
            return jsonify({
                'message': 'Delete successfully.',
                'id': bid,
                'url': url
            }), HTTP_200_OK
        case 'PUT' | 'PATCH':
            body = request.get_json().get('body')
            url = request.get_json().get('url')

            if not validators.url(url):
                return jsonify({'message': 'Invalid URL'}), HTTP_400_BAD_REQUEST

            bookmark_item.url = url
            bookmark_item.body = body
            data['url'] = bookmark_item.url
            data['body'] = bookmark_item.body

            db.session.commit()

            return jsonify(data), HTTP_200_OK


@bookmarks.get('/stats')
@jwt_required()
@swag_from('./docs/bookmarks/stats.yml')
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()
    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url
        }

        data.append(new_link)
    return jsonify({
        'data': data
    }), HTTP_200_OK
