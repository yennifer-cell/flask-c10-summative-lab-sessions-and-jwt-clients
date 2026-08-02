from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_digest = db.Column(db.String(128), nullable=False)

    notes = db.relationship("Note", back_populates="user", cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, password):
        from extensions import bcrypt

        self.password_digest = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        from extensions import bcrypt

        return bcrypt.check_password_hash(self.password_digest, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
        }


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "mood": self.mood,
            "user_id": self.user_id,
        }
