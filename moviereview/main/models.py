from mongoengine import Document, fields
from django.conf import settings
import hashlib


class User(Document):
    email = fields.EmailField(required=True)
    password = fields.StringField(required=True)

    def set_password(self, password: str) -> None:
        hashed_password = hashlib.sha512((settings.SECRET_KEY + password).encode()).hexdigest()
        self.password = hashed_password
        self.save()

    def verify_password(self, password: str) -> bool:
        hashed_password = hashlib.sha512((settings.SECRET_KEY + password).encode()).hexdigest()
        if self.password == hashed_password:
            return True
        else:
            return False


class Session(Document):
    user = fields.ReferenceField(User, required=True)
    session_id = fields.StringField(required=True)

    def generate_session_id(self) -> None:
        session_id = hashlib.sha512((settings.SECRET_KEY + self.user.email).encode()).hexdigest()
        self.session_id = session_id
        self.save()

    @classmethod
    def get_user_data(cls, session_id: str):
        session = cls.objects(session_id=session_id).first()
        if session:
            return session.user


class Review(Document):
    author = fields.ReferenceField(User, required=True)
    movie = fields.StringField(required=True)
    text = fields.StringField(required=True)
    comments = fields.ListField(fields.ReferenceField('Comment'), required=False, null=False, default=[])


class Comment(Document):
    review = fields.ReferenceField(Review, required=True)
    author = fields.ReferenceField(User, required=True)
    text = fields.StringField(required=True)


