from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    def validate_name(self, key, name):
        if not name or name.strip() == "":
            raise ValueError("Author must have a name.")
        
        existing_author = Author.query.filter_by(name=name).first()
        if existing_author and existing_author.id != self.id:
            raise ValueError("Author name must be unique.")
        return name

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be exactly 10 digits.")
        return value

    def __repr__(self):
        return f"<Author id={self.id} name={self.name}>"

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    summary = db.Column(db.String)
    category = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', backref='posts')

    # Patterns to catch clickbait (matches are case-insensitive)
    CLICKBAIT_PATTERNS = [
        r'\bsecret\b',
        r'\byou won\'?t believe\b',
        r'\bamazing\b',
        r'\bshocking\b',
        r'\btop \d+\b'
    ]

    @validates('title')
    def validate_title(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Post must have a title.")
        
        normalized = value.lower()
        for pattern in self.CLICKBAIT_PATTERNS:
            if re.search(pattern, normalized):
                raise ValueError("Post title cannot be clickbait.")
        return value

    @validates('content')
    def validate_content(self, key, value):
        if not value or len(value.strip()) < 250:
            raise ValueError("Post content must be at least 250 characters.")
        return value

    @validates('summary')
    def validate_summary(self, key, value):
        if value and len(value.strip()) > 250:
            raise ValueError("Summary must be no longer than 250 characters.")
        return value

    @validates('category')
    def validate_category(self, key, value):
        valid_categories = ['Technology', 'Lifestyle', 'Education', 'Health', 'Finance', 'Non-Fiction']
        if value and value not in valid_categories:
            raise ValueError(f"Category must be one of the following: {', '.join(valid_categories)}.")
        return value

    def __repr__(self):
        return f"<Post id={self.id} title={self.title}>"
