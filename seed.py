from faker import Faker

from app import create_app
from extensions import db
from models import User, Note


def seed():
    app = create_app()
    fake = Faker()

    with app.app_context():
        db.drop_all()
        db.create_all()

        users = []
        for i in range(3):
            user = User(username=f"user{i+1}")
            user.password = "password"
            db.session.add(user)
            users.append(user)

        db.session.commit()

        for user in users:
            for _ in range(5):
                note = Note(
                    title=fake.sentence(nb_words=5),
                    content=fake.paragraph(nb_sentences=3),
                    mood=fake.random_element(elements=("productive", "tired", "focused", "relaxed")),
                    user_id=user.id,
                )
                db.session.add(note)

        db.session.commit()
        print("Seed data created.")


if __name__ == "__main__":
    seed()
