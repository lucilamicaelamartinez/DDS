from flask import request, jsonify, Blueprint
from .. import db
from main.models import UserModel
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, jwt_optional
from main.mail.functions import sendMail

auth = Blueprint('auth', __name__, url_prefix= '/auth')

@auth.route('/login', methods = ['POST'])
def login():
    user = db.session.query(UserModel).filter(UserModel.email == request.get_json().get('email')).first_or_404()
    if user.validate_pass(request.get_json().get('password')):
        access_token = create_access_token(identity = user)
        data = '{"id":"'+str(user.id)+'", "email":"'+str(user.email)+'", "access_token":"'+access_token+'"}'
        return  data, 200
    else:
        return 'Incorrect password', 204
@auth.route('/register', methods = ['POST'])
def register():
    user = UserModel.from_json(request.get_json())
    exists = db.session.query(UserModel).filter(UserModel.id == user.id).scalar() is not None
    if exists:
        return 'Duplicate email', 409
    else:
        try:
            db.session.add(user)
            sent = sendMail(user.email,"Register",'mail/register', user = user)
            if sent == True:
                db.session.commit()
            else:
                db.session.rollback()
                return str(sent), 502
        except Exception as error:
            db.session.rollback()
            return str(error), 409
        return user.to_json(), 201