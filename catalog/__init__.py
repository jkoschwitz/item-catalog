import os
from database_setup import Base, User, Category, Book
from datetime import datetime
from database_helpers import *
from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from flask.ext.github import GitHub
from flask.ext.seasurf import SeaSurf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

app = Flask(__name__)
app.debug = True

APP_SECRET_KEY = (os.environ['APP_SECRET_KEY']
                  if 'APP_SECRET_KEY' in os.environ else 'secret')
GITHUB_CLIENT_ID = (os.environ['GITHUB_CLIENT_ID']
                    if 'GITHUB_CLIENT_ID' in os.environ else None)
GITHUB_CLIENT_SECRET = (os.environ['GITHUB_CLIENT_SECRET']
                        if 'GITHUB_CLIENT_SECRET' in os.environ else None)

app.secret_key = APP_SECRET_KEY
app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET

github = GitHub(app)

# SeaSurf is a Flask extention to prevent cross-site request forgeries (CSRF)
csrf = SeaSurf(app)


@app.before_request
def before_request():
    # Make user data available to all templates
    if 'user_id' in session:
        g.user = db_session.query(User).get(session['user_id'])

    # Make helper functions available to all templates
    g.authenticated = authenticated
    g.can_edit = can_edit


# ##############################################################################
# ROUTES

@app.route('/')
def index():
    # Homepage page, list all books, option to add book if logged in
    return render_template('book-list.html',
                           category_list=category_all(),
                           book_list=db_session.query(Book).all(),
                           title='All Books')


@app.route('/categories/<int:category_id>', methods=['GET'])
def categories(category_id):
    # List books with in category, option to add book if logged in
    return render_template('book-list.html',
                           category_list=category_all(),
                           book_list=books_in_category(category_id),
                           title=category_name(category_id))


@app.route('/book/<int:book_id>', methods=['GET'])
def book(book_id):
    # show book info, option to edit/delete if owner
    book = db_session.query(Book).filter_by(id=book_id).one()
    return render_template('book-view.html',
                           book=book,
                           title=book.title)


# ##############################################################################
# Book: Add, Edit, and Delete

@app.route('/book/new', methods=['GET', 'POST'])
def new_book():
    # Book creation

    # Ensure User is logged in and authenticated
    if not authenticated():
        return redirect(url_for('signin'))

    if request.method == 'POST':
        # Parse form for book data
        book = parse_book_form(request.form)
        # Assign seesion user as owner (used for edit/delete permission)
        book.user_id = session['user_id']
        # Save new book in DB and redirect User to Book main page
        db_session.add(book)
        db_session.commit()
        flash('New book added!', 'success')
        return redirect(url_for('book', book_id=book.id))
    else:
        return render_template('book-edit.html',
                               title='New Book',
                               category_list=category_all(),
                               book={})


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    # Book editing

    # Select book from DB on book_id
    book = db_session.query(Book).filter_by(id=book_id).one()

    if request.method == 'POST':
        # Ensure User is logged in and authenticated
        if not authenticated():
            return redirect(url_for('signin'))

        # Check User has permission to edit book
        if not can_edit(book):
            flash('You do not have permission to edit this)', 'warning')
            return redirect(url_for('book', book_id=book_id))

        # User is authenticated and authorised, parse form for edited data
        book_data = parse_book_form(request.form)

        # Update book and redirect User to the Book main page
        book.title = book_data.title
        book.author = book_data.author
        book.url = book_data.url
        book.thumbnail_url = book_data.thumbnail_url
        book.isbn = book_data.isbn
        book.description = book_data.description
        book.publish_date = book_data.publish_date
        book.category_id = book_data.category_id

        db_session.add(book)
        db_session.commit()
        flash('Changes saved!', 'success')
        return redirect(url_for('book', book_id=book_id))
    else:
        return render_template('book-edit.html',
                               title='Edit Book',
                               category_list=category_all(),
                               book=book)


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(book_id):
    # Book deletion

    # Select book from DB on book_id
    book = db_session.query(Book).filter_by(id=book_id).one()

    if request.method == 'POST':
        # Ensure User is logged in and authenticated
        if not authenticated():
            return redirect(url_for('signin'))

        # Check User has permission to delete book
        if not can_edit(book):
            flash('You do not have permission to edit this)', 'warning')
            return redirect(url_for('book', book_id=book_id))

        # User is authenticated and authorised, delete book and redirect User
        # to the Homepage
        db_session.delete(book)
        db_session.commit()
        flash('Book was deleted.', 'success')
        return redirect(url_for('index'))

    else:
        return render_template('book-delete.html',
                               title='Delete Book',
                               category_list=category_all(),
                               book=book)


# ##############################################################################
# OAUTH

@app.route('/signin')
def signin():
    # Authorize user with GitHub's OAuth
    return github.authorize()


@app.route('/signout')
def signout():
    # Signout user, remove session data, and redirct to index
    session.pop('user_id', None)
    session.pop('access_token', None)
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    # Callback from github oauth
    next_url = request.args.get('next') or url_for('index')

    # Ensure Auth token is present
    if oauth_token is None:
        flash('Authorization failed.', 'danger')
        return redirect(next_url)

    # Search for user in DB based on Auth token
    user = db_session.query(User).filter_by(access_token=oauth_token).first()

    if user is None:
        # If user is not found in DB create new user with Auth token
        user = User(oauth_token)

    # Retrive Users GitHub Data and assign name to user.username as this may
    # have changed since last log in
    github_params = {'access_token': oauth_token}
    github_response = github.raw_request('GET', 'user', params=github_params)
    github_user_data = github_response.json()
    user.username = str(github_user_data['login'])

    # Update DB with new/updated User
    db_session.add(user)
    db_session.commit()

    # store user id and access token in session
    session['user_id'] = user.id
    session['user_token'] = user.access_token

    flash('You are logged in.', 'success')
    return redirect(next_url)


# ##############################################################################
# JSON API

@app.route('/categories.json', methods=['GET'])
def api_categories():
    # return JSON object of all categories
    return jsonify(category_list=[category.serialize for
                                  category in category_all()])


@app.route('/categories/<int:category_id>.json', methods=['GET'])
def api_books_in_category(category_id):
    # return JSON object of books within a given category
    return jsonify(books=[book.serialize for
                          book in books_in_category(category_id)])


@app.route('/book/<int:book_id>.json', methods=['GET'])
def api_book(book_id):
    # return JSON object of book info for a given book ID
    book = db_session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=[book.serialize])
