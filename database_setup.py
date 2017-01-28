import os
from sqlalchemy import (create_engine, Column, ForeignKey, Integer, String,
                        Date, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

DATABASE_URL = (os.environ['DATABASE_URL']
                if 'DATABASE_URL' in os.environ else 'postgresql:///catalog')

engine = create_engine(DATABASE_URL)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    access_token = Column(String(200))

    def __init__(self, access_token):
        self.access_token = access_token


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    books = relationship('Book', cascade='all, delete-orphan')

    @property
    def serialize(self):
        ''' JSON serializer method '''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    url = Column(String(255))
    thumbnail_url = Column(String(255))
    isbn = Column(String(20))
    description = Column(String(1000))
    publish_date = Column(Date)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        ''' JSON serializer method '''
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'isbn': self.isbn,
            'description': self.description,
            'publish_date': str(self.publish_date.isoformat()),
            'category_id': self.category_id
        }

Base.metadata.create_all(engine)
db_session = sessionmaker(bind=engine)()

# Populate database if empty
if db_session.query(Category).first() == None:
    # load data from JSON file
    with open('import.json', 'rb') as file:
        data = json.load(file)

    # Loop through 'category-list' data, create 'Category' object for each
    # iteration and store in database
    for item in data['category-list']:
        category = Category(name=item['name'])
        db_session.add(category)

    # Loop through 'book-list' data, create 'Book' object for each iteration
    # and store in database
    for item in data['book-list']:
        book = Book(title=item['title'],
                    author=item['author'],
                    url=item['url'],
                    thumbnail_url=item['thumbnail_url'],
                    isbn=item['isbn'],
                    description=item['description'],
                    publish_date=datetime.strptime(item['publish_date'],
                                                   '%Y-%m-%d'),
                    category_id=item['category_id'])
        db_session.add(book)

    # Commit imported data to database
    db_session.commit()

    # Display messgae to console to verify import in complete
    print "import complete"
