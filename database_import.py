from database_setup import Category, Book, db_session
from datetime import datetime
import json

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
