from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.const.http_status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.database import User, db
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token
from flasgger import swag_from

auth = Blueprint('auth', __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
@swag_from('./docs/auth/register.yml')
def registration():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if len(password) < 6:
        return jsonify({
            'error': 'Password is too short'
        }), HTTP_400_BAD_REQUEST
    if len(username) < 4:
        return jsonify({
            'error': 'Username is too short'
        }), HTTP_400_BAD_REQUEST
    elif not username.isalnum() or " " in username:
        return jsonify({
            'error': 'Username is must be alphabetic with numbers, also no space'
        }), HTTP_400_BAD_REQUEST

    # if email.find('@') == -1 and email.find('.') == -1:
    if not validators.email(email):
        return jsonify({
            'error': 'Email invalid.'
        }), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already in use'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username already in use'}), HTTP_400_BAD_REQUEST

    pass_hash = generate_password_hash(password)

    user = User(username=username, email=email, password=pass_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully!',
        'user': {
            'username': username,
            'email': email
        }
    }), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yml')
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)
            return jsonify({
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'access': access,
                    'refresh': refresh,
                }
            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), \
        HTTP_401_UNAUTHORIZED


@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'user': {
            'username': user.username,
            'email': user.email
        },
        'message': 'Login successful!'
    }), HTTP_200_OK


@auth.get('/token/refresh/')
@jwt_required(refresh=True)
def refresh_user_token():
    identify = get_jwt_identity()
    access = create_access_token(identity=identify)

    return jsonify({
        'new_token': access
    }), HTTP_200_OK
