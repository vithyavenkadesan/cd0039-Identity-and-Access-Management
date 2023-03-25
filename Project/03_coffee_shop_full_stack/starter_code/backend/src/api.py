import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)

with app.app_context():
    db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_all_drinks():
        drinks = Drink.get_drinks_short()
        return jsonify(
            {
                "success": True,
                "drinks": drinks
            }
        )

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinksDetail(payload):
        drinks = Drink.get_drinks_long()
        return jsonify(
            {
                "success": True,
                "drinks": drinks
            }
        )

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
        body = request.get_json()
        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)
        try:
            drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
            drink.insert()
            created_drink = [drink.long()]
            return jsonify(
                {
                    "success": True,
                    "drinks": created_drink
                }
            )

        except:
            print(sys.exc_info())
            abort(500)

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
        body = request.get_json()
        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)
        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink is None:
                abort(404)
            if new_title:
                drink.title = new_title
            if new_recipe:
                drink.recipe =  json.dumps(new_recipe)
            drink.update()
            updated_drink = [drink.long()]
            return jsonify(
                {
                    "success": True,
                    "drinks": updated_drink
                }
            )

        except:
            print(sys.exc_info())
            abort(500)

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink is None:
                abort(404)
            drink.delete()
            return jsonify(
                {
                    "success": True,
                    "delete": id
                }
            )

        except:
            print(sys.exc_info())
            abort(500)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal error"
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(401)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorised"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403
