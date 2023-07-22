from flask import Flask
from flask_restful import Api
from resources.hotel import Hoteis, Hotel
from resources.usuario import Usuario, UserRegister, UserLogin, UserLogout
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'MeuSegredo2302'
app.config['JWT_BLACKLIST_ENABLED'] = True
api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader  # Verificar se o token está na blacklist
def verificar_blacklist(token):
    return token['jti'] in BLACKLIST


@jwt.revoked_token_loader  # Acesso revogado
def token_invalidado():
    return jsonify({'message': 'Your have been logged out'}), 401


@app.before_request
def criar_banco():
    banco.create_all()


api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:identification>')
api.add_resource(Usuario, '/usuario/<int:user_id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    from sql_alchemy import banco

    banco.init_app(app)
    app.run(debug=True)
