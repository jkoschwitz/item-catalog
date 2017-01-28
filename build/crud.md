# Operations with SQLAlchemy

## SETUP

1. First import the necessary libraries
2. Connect to database file
3. Create a database session to interface with the database

```py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db = sessionmaker(bind=engine)()
```

## CREATE

Create Category:

```py
category_Database = Category(name='Database')
db.add(category_Database)
db.commit()
```


Create Book and add to Category:

```py
book_Database = Book(name='Database Book',
                     description='...',
                     category=category_Database)
db.add(book_Database)
db.commit()
```


## READ

Read out information from database using the query method in SQLAlchemy:

```py
first_result = db.query(Category).first()
one_result = db.query(Book).filter_by(category_id=first_result.id)
all_results = db.query(Book).all()

for item in all_results:
    print item.id
```


## UPDATE

1. Find entry
2. Edit value(s)
3. Add to database session
4. Commit to database

```py
book_1 = db.query(Book).filter_by(id=1).one()
book_1.description = '...'
db.add(book_1)
db.commit()
```


## DELETE

1. Find entry
2. Delete from database session
3. Commit to database

```py
book_1 = db.query(Book).filter_by(id=1).one()
db.delete(book_1)
db.commit()
```
