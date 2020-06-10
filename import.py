import os
import csv,requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_tables():
    with open('SCHEMA.sql','r',newline='') as f:
        commands = [i.strip() for i in f.read().split(';')]
        for command in commands:
            print(command)
            db.execute(command)
        db.commit()

def get_books_data():
    with open('books.csv','r',newline='') as rf:
        csvfile = csv.reader(rf)
        next(csvfile)
        while csvfile:
            frame = {}
            try:
                for i in range(500):
                    row = next(csvfile)
                    frame[row[0]] = row
            except StopIteration :
                break

            isbns = ','.join(frame)

            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6ptJdBeyhCL2l0nTBXeLg", "isbns": isbns})
            data = res.json()['books']
            for book in data:
                yield [ *frame[book['isbn']], book['work_reviews_count'], book['average_rating']]


def insert_books():
    cnt = 0
    items = get_books_data()
    for item in items:
        isbn, title, author, year, reviews_count, average_rating = item
        db.execute(
            'INSERT INTO books (isbn, title, author, year, reviews_count, average_rating)'
            ' VALUES (:isbn, :title, :author, :year, :reviews_count, :average_rating)',
            {
                'isbn':isbn,
                'title':title,
                'author':author,
                'year':year,
                'reviews_count':reviews_count,
                'average_rating':average_rating
            }
        )
        cnt+=1
        if cnt%100==0:
            db.commit()
    db.commit()
def commands():
    print(db.execute(
        'SELECT * '
        'FROM reviews '
    ).fetchall())
commands()
command=0
cmd = 0
if command :
    create_tables()

if cmd :
    insert_books()
        # 'SELECT '
	    #    'COLUMN_NAME '
        #    'FROM '
	    #       'information_schema.COLUMNS '
        #       'WHERE '
	# " TABLE_NAME = 'reviews'"
