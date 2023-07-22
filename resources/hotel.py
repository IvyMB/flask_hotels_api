from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3


def normalize_params(cidade=None, estrelas_min=0, estrelas_max=5, diaria_min=0, diaria_max=10000,
                     limit=50, offset=0, **dados):
    if cidade:
        return {'estrelas_min': estrelas_min, 'estrelas_max': estrelas_max, 'diaria_min': diaria_min,
                'diaria_max': diaria_max, 'cidade': cidade, 'limit': limit, 'offset': offset}

    # Retornar todos menos a cidade
    return {'estrelas_min': estrelas_min, 'estrelas_max': estrelas_max, 'diaria_min': diaria_min,
            'diaria_max': diaria_max, 'limit': limit, 'offset': offset}


path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=int)
path_params.add_argument('offset', type=int)


class Hoteis(Resource):
    def get(self):
        params_received = path_params.parse_args()
        # Pegando apenas as chaves e valores que não estão vazios
        valid_data = {key: params_received[key] for key in params_received if params_received[key] is not None}

        params = normalize_params(**valid_data)
        conn = sqlite3.connect('hotel_services.db')
        cursor = conn.cursor()

        if not params.get('cidade'):
            query = "SELECT * FROM hoteis " \
                    "WHERE (estrelas > ? AND estrelas < ?) " \
                    "AND (diaria > ? AND diaria < ?) " \
                    "AND cidade = ?" \
                    "LIMIT ? OFFSET ?"
            tupla = tuple([params[key] for key in params])
            result = cursor.execute(query, tupla)

        else:
            query = "SELECT * FROM hoteis " \
                    "WHERE (estrelas > ? AND estrelas < ?) " \
                    "AND (diaria > ? AND diaria < ?) " \
                    "LIMIT ? OFFSET ?"
            tupla = tuple([params[key] for key in params])
            result = cursor.execute(query, tupla)

        # Retornando os valores de resultado em uma lista
        hoteis = []
        for linha in result:
            hoteis.append({
                'hotel_id': linha[0],
                'nome': linha[1],
                'estrelas': linha[2],
                'valor_diaria': linha[3],
                'cidade': linha[4]
            })

        return {'hoteis': hoteis}


class Hotel(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('nome', type=str, required=True, help='Name is required.')
        self.reqparse.add_argument('estrelas', type=float, required=True, help='Stars is required.')
        self.reqparse.add_argument('valor_diaria', type=float, required=True, help='Daily value is required.')
        self.reqparse.add_argument('cidade', type=str, required=True, help='City is required.')

    def get(self, identification):
        hotel = HotelModel.find_hotel(identification)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found'}, 404

    @jwt_required
    def post(self, identification):
        if HotelModel.find_hotel(identification):
            return {'message': 'Error to create the new hotel, the id already exists'}, 400  # Bad request

        data = self.reqparse.parse_args()
        hotel = HotelModel(int(identification), **data)
        hotel.save_hotel()

        return hotel.json()

    @jwt_required
    def put(self, identification):
        data = self.reqparse.parse_args()

        hotel_finded = HotelModel.find_hotel(identification)
        if hotel_finded:
            hotel_finded.update_hotel(**data)
            hotel_finded.save_hotel()
            return hotel_finded.json(), 200

        # Hotel não encontrado
        hotel = HotelModel(identification, **data)
        hotel.save_hotel()
        return hotel.json(), 201

    @jwt_required
    def delete(self, identification):
        hotel = HotelModel.find_hotel(identification)
        if hotel:
            hotel.delete_hotel()
            return {'message': 'Hotel deleted'}
        return {'message': 'Hotel not found'}, 404
