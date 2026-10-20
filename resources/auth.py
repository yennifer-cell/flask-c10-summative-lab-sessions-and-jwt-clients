from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models import User


class SignupResource(Resource):
    def post(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"errors": ["A JSON object is required."]}, 400

        username = data.get("username")
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")

        errors = []
        if not isinstance(username, str) or not username.strip():
            errors.append("Username is required.")
        elif len(username.strip()) > 80:
            errors.append("Username must be 80 characters or fewer.")
        if not isinstance(password, str) or not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        elif len(password.encode("utf-8")) > 72:
            errors.append("Password must be 72 bytes or fewer.")
        if password != password_confirmation:
            errors.append("Password confirmation does not match.")

        username = username.strip() if isinstance(username, str) else username
        if username and User.query.filter_by(username=username).first():
            errors.append("Username has already been taken.")

        if errors:
            return {"errors": errors}, 400

        user = User(username=username)
        user.password = password
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        return {"token": access_token, "user": user.to_dict()}, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"errors": ["A JSON object is required."]}, 400

        username = data.get("username")
        password = data.get("password")

        user = (
            User.query.filter_by(username=username).first()
            if isinstance(username, str) and isinstance(password, str)
            else None
        )
        if not user or not user.check_password(password):
            return {"errors": ["Invalid username or password."]}, 401

        access_token = create_access_token(identity=str(user.id))
        return {"token": access_token, "user": user.to_dict()}, 200


class MeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user:
            return {"errors": ["User not found."]}, 404

        return user.to_dict(), 200
