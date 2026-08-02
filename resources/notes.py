from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Note


class NoteListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

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
        data = request.get_json() or {}
        title = data.get("title")
        content = data.get("content")
        mood = data.get("mood")

        errors = []
        if not title:
            errors.append("Title is required.")
        if not content:
            errors.append("Content is required.")

        if errors:
            return {"errors": errors}, 400

        note = Note(title=title, content=content, mood=mood, user_id=user_id)
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

        data = request.get_json() or {}
        title = data.get("title")
        content = data.get("content")
        mood = data.get("mood")

        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if mood is not None:
            note.mood = mood

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
