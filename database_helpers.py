from database_setup import User, Category, Book, db_session
from datetime import datetime
from flask import flash, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import bleach


def parse_book_form(form):
    # Returns a new Book object created from form data
    form = dict(form)
    book = Book(title=bleach.clean(form['book_title'][0]),
                author=bleach.clean(form['book_author'][0]),
                url=bleach.clean(form['book_url'][0]),
                thumbnail_url=bleach.clean(form['book_thumbnail_url'][0]),
                isbn=bleach.clean(form['book_isbn'][0]),
                description=bleach.clean(form['book_description'][0]),
                category_id=bleach.clean(form['book_category'][0]),
                publish_date=(datetime
                              .strptime(bleach.clean(form['book_published'][0]), '%Y-%m-%d'))
                )
    return book


def authenticated():
    # Returns whether or not the session user is authenticated
    if 'user_id' in session and 'user_token' in session:
        user = db_session.query(User).filter_by(id=session['user_id']).first()
        if user:
            return user.access_token == session['user_token']
    return False


def can_edit(book):
    # returns whether the book is owned by the session user
    if authenticated():
        if book.user_id is None:
            return False
        else:
            return ('user_id' in session and
                    book.user_id == session['user_id'])
    else:
        return False


def category_name(category_id):
    # Return the name for a corresponding category id
    category = db_session.query(Category).filter_by(id=category_id).one()
    return category.name


def category_all():
    # convienience function to return all category data
    return db_session.query(Category).all()


def books_in_category(category_id):
    # Return all Books for a corresponding Category
    return (db_session.query(Book)
            .filter_by(category_id=category_id)
            .order_by(Book.publish_date))
