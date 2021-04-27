from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    feedback = db.relationship("Feedback", backref="user", cascade="all, delete-orphan")

    # User Model Representation
    def __repr__(self):
        u = self
        return f"<User username={u.username} email={u.email} first_name={u.first_name} last_name={u.last_name} is_admin={u.is_admin}>"


    # User Registration
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name, is_admin):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        # return instance of user with username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, is_admin=is_admin)


    # User Authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct, 
        Return user if valid; else return False"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            # return user instance
            return user
        else:
            return False



class Feedback(db.Model):
    """Feedback Model"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'))

    # Feedback Model Representation
    def __repr__(self):
        f = self
        return f"<Feedback id={f.id} title={f.title} content={f.content} user={f.username} >"

