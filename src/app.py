"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_users():
    print('get users')
    all_users = User.query.all()
    print(all_users)
    results = list(map(lambda user: user.serialize(), all_users))
    print(results)

    response_body = {
        "msg": "Estos son los usuarios",
        "users": results
    }
    return jsonify(response_body), 200


@app.route('/character', methods=['GET'])
def get_characters():
    all_characters = Character.query.all()
    results = list(
        map(lambda character: character.serialize(), all_characters))

    return jsonify(results), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    results = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify(results), 200


@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.filter_by(id=character_id).first()

    return jsonify(character.serialize()), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()

    return jsonify(planet.serialize()), 200


@app.route('/planet', methods=['POST'])
def add_planet():
    body = request.get_json()
    planet = Planet(**body)
    db.session.add(planet)
    db.session.commit()

    response_body = {
        "planet created succesfully": planet.serialize()
    }

    return jsonify(response_body), 200


@app.route('/character', methods=['POST'])
def add_character():
    body = request.get_json()
    character = Character(**body)
    db.session.add(character)
    db.session.commit()

    response_body = {
        "character created succesfully": character.serialize()
    }

    return jsonify(response_body), 200


@app.route('/user/<int:user_id>/favorite_character', methods=['GET'])
def get_favorite_character(user_id):
    all_favorite_characters = FavoriteCharacter.query.filter_by(user_id = user_id).all()
    results = list(map(lambda favorite_character: favorite_character.serialize(), all_favorite_characters))

    return jsonify(results), 200

@app.route('/user/<int:user_id>/favorite_planet', methods=['GET'])
def get_favorite_planet(user_id):
    all_favorite_planets = FavoritePlanet.query.filter_by(user_id = user_id).all()
    results = list(map(lambda favorite_planet: favorite_planet.serialize(), all_favorite_planets))

    return jsonify(results), 200


@app.route('/user/<int:user_id>/favorite_character/character/<int:id>', methods=['POST'])
def add_favorite_character(user_id,id):
    print(add_favorite_character)
    # user = User.query.get(user_id)
    # character = Character.query.get(id)

    # if id is id:
    #     return jsonify({"Error":"Character already exist"})
    new_favorite_character = FavoriteCharacter(user_id = user_id, character_id = id)
    db.session.add(new_favorite_character)
    db.session.commit()

    return jsonify(new_favorite_character.serialize()), 200

@app.route('/user/<int:user_id>/favorite_planet/planet/<int:id>', methods=['POST'])
def add_favorite_planet(user_id,id):
    print(add_favorite_planet)
    # user = User.query.get(user_id)
    # planet = Planet.query.get(id)

    # if id is id:
    #     return jsonify({"Error":"Planet already exist"})
    new_favorite_planet = FavoritePlanet(user_id = user_id, planet_id = id)
    db.session.add(new_favorite_planet)
    db.session.commit()

    return jsonify(new_favorite_planet.serialize()), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
