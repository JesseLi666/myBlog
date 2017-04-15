from datetime import datetime
from markdown import markdown
import bleach
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from flask_login import UserMixin
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# post_pic_relationship = db.Table('pp',
#     db.Column('post', db.String(10), db.ForeignKey('pics.id')),
#     db.Column('pic', db.String(10), db.ForeignKey('posts.id'))
# )

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    abstract = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(128))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    # pic = db.relationship('Pic', secondary=post_pic_relationship,
    #                       backref=db.backref('post', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            'img':['src', 'alt', 'class']
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True))

        abstract_allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'p']
        target.abstract = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=abstract_allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    url_t = db.Column(db.String(64))
    filename = db.Column(db.String(64))
    filename_t = db.Column(db.String(64))
    about = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    thumbnail_url = db.Column(db.String(128))
    abstract = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
