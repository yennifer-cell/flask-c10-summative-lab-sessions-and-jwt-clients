from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Note


class NoteListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return {"errors": ["Page and per_page must be integers."]}, 400
        if page < 1 or per_page < 1 or per_page > 100:
            return {"errors": ["Page must be positive and per_page must be between 1 and 100."]}, 400

        query = Note.query.filter_by(user_id=user_id).order_by(Note.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        notes = [note.to_dict() for note in pagination.items]
        return {
            "notes": notes,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"errors": ["A JSON object is required."]}, 400

        title = data.get("title")
        content = data.get("content")
        mood = data.get("mood")

        errors = []
        if not isinstance(title, str) or not title.strip():
            errors.append("Title is required.")
        elif len(title.strip()) > 140:
            errors.append("Title must be 140 characters or fewer.")
        if not isinstance(content, str) or not content.strip():
            errors.append("Content is required.")
        if mood is not None and not isinstance(mood, str):
            errors.append("Mood must be a string.")
        elif isinstance(mood, str) and len(mood.strip()) > 50:
            errors.append("Mood must be 50 characters or fewer.")

        if errors:
            return {"errors": errors}, 400

        note = Note(
            title=title.strip(),
            content=content.strip(),
            mood=mood.strip() if isinstance(mood, str) else None,
            user_id=user_id,
        )
        db.session.add(note)
        db.session.commit()

        return note.to_dict(), 201


class NoteResource(Resource):
    @jwt_required()
    def patch(self, note_id):
        user_id = int(get_jwt_identity())
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return {"errors": ["Note not found."]}, 404

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"errors": ["A JSON object is required."]}, 400

        errors = []
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                errors.append("Title must be a non-empty string.")
            elif len(title.strip()) > 140:
                errors.append("Title must be 140 characters or fewer.")
        if "content" in data:
            content = data["content"]
            if not isinstance(content, str) or not content.strip():
                errors.append("Content must be a non-empty string.")
        if "mood" in data:
            mood = data["mood"]
            if mood is not None and not isinstance(mood, str):
                errors.append("Mood must be a string or null.")
            elif isinstance(mood, str) and len(mood.strip()) > 50:
                errors.append("Mood must be 50 characters or fewer.")

        if errors:
            return {"errors": errors}, 400

        if "title" in data:
            note.title = data["title"].strip()
        if "content" in data:
            note.content = data["content"].strip()
        if "mood" in data:
            mood = data["mood"]
            note.mood = mood.strip() if isinstance(mood, str) else None

        db.session.commit()
        return note.to_dict(), 200

    @jwt_required()
    def delete(self, note_id):
        user_id = int(get_jwt_identity())
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return {"errors": ["Note not found."]}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204
