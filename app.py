from flask import Flask, jsonify
from flask_restful import Api

from config import Config
from extensions import bcrypt, db, jwt, migrate
from resources.auth import LoginResource, SignupResource, MeResource
from resources.notes import NoteListResource, NoteResource


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    api = Api(app)
    api.add_resource(SignupResource, "/signup")
    api.add_resource(LoginResource, "/login")
    api.add_resource(MeResource, "/me")
    api.add_resource(NoteListResource, "/notes")
    api.add_resource(NoteResource, "/notes/<int:note_id>")

    @app.route("/")
    def health_check():
        return jsonify({"message": "API is running"}), 200

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
