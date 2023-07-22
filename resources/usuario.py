from flask_restful import Resource, reqparse
from models.usuario import UsuarioModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from blacklist import BLACKLIST

arguments = reqparse.RequestParser()
arguments.add_argument('login', type=str, required=True, help='The field login can not be left blank')
arguments.add_argument('password', type=str, required=True, help='The field password can not be left blank')


class Usuario(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('login', type=float, required=True, help='The field login can not be left blank')
        self.reqparse.add_argument('password', type=float, required=True, help='The field password can not be left blank')

    @jwt_required
    def get(self, user_id):
        user = UsuarioModel.find_user(user_id)
        if user:
            return user.json(), 202
        return {'message': 'User not found'}, 404

    @jwt_required
    def delete(self, user_id):
        user = UsuarioModel.find_user(user_id)
        if user:
            user.delete_hotel()
            return {'message': 'User deleted'}, 202
        return {'message': 'User not found'}, 404


class UserRegister(Resource):
    def post(self):
        data = arguments.parse_args()

        if UsuarioModel.find_by_login(data['login']):
            return {"message": "User with login '{}' already exists.".format(data['login'])}, 200

        user = UsuarioModel(**data)
        user.save_user()
        return {"message": "User created succesfully"}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = arguments.parse_args()
        user = UsuarioModel.find_by_login(data['login'])
        if user and user.password == data['password']:
            access_token = create_access_token(identity=user.login)
            return access_token, 200
        return {'message': 'the username or the password is wrong'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jwt_id = get_jwt_identity
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged out successfully'}, 200
