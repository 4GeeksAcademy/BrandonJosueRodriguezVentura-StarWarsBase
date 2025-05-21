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
from models import db, User, Character, Planet, Vehicle, Climate, Gender
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to the Star Wars API"}), 200


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()

    required_fields = ['name', 'size', 'climate', 'gravity']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        new_planet = Planet(
            name=data['name'],
            size=data['size'],
            climate=Climate[data['climate'].upper()],
            gravity=bool(data['gravity'])
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(new_planet.serialize()), 201
    except KeyError:
        return jsonify({"error": "Invalid climate type"}), 400
    
@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()

    required_fields = ['name', 'age', 'gender']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        new_character = Character(
            name=data['name'],
            age=data['age'],
            gender=Gender[data['gender'].upper()]
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify(new_character.serialize()), 201
    except KeyError:
        return jsonify({"error": "Invalid gender type"}), 400


@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([c.serialize() for c in characters]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User(
        name=data.get("name", ""),
        lastname=data.get("lastname", ""),
        email=data["email"],
        password=data["password"],
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created", "user": user.serialize()}), 201


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "favorite_planets": [p.serialize() for p in user.favorite_planets],
        "favorite_characters": [c.serialize() for c in user.favorite_characters],
        "favorite_vehicles": [v.serialize() for v in user.favorite_vehicles]
    }), 200


@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['POST'])
def add_fav_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    if planet in user.favorite_planets:
        return jsonify({"msg": "Planet already in favorites"}), 400

    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify({"msg": f"Planet (id={planet_id}) added to user (id={user_id}) favorites"}), 200


@app.route('/favorite/people/<int:user_id>/<int:people_id>', methods=['POST'])
def add_fav_character(people_id, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error":"User not found"}), 404
    
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    if character in user.favorite_characters:
        return jsonify({"msg": "Character already in favorites"}), 400

    user.favorite_characters.append(character)
    db.session.commit()
    return jsonify({"msg": "Character added to favorites"}), 200


@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def remove_fav_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    if planet in user.favorite_planets:
        user.favorite_planets.remove(planet)
        db.session.commit()
        return jsonify({"msg": f"Planet (id={planet_id}) removed from user (id={user_id}) favorites"}), 200
    
    return jsonify({"error": "Planet not in favorites"}), 404


@app.route('/favorite/people/<int:user_id>/<int:people_id>', methods=['DELETE'])
def remove_fav_character(user_id, people_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    if character in user.favorite_characters:
        user.favorite_characters.remove(character)
        db.session.commit()
        return jsonify({"msg": f"Character (id={people_id}) removed from user (id={user_id}) favorites"}), 200
    
    return jsonify({"error": "Character not in favorites"}), 404

if __name__ == '__main__':
    app.run(debug=True)