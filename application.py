import os
from functools import wraps

from flask import Flask, session, request, render_template, url_for, redirect, g, make_response,flash,Markup,jsonify
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash(f"Please login to use '{view.__name__.replace('_',' ')}' function")
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view

@app.before_request
def load_loggedin_user():
    user_id = session.get('user_id',None)
    g.user = None
    if user_id is not None:
        g.user = db.execute(
            'SELECT * FROM users WHERE id = :id',
            {'id':user_id}
        ).fetchone()

def error404():
        error = {
            'code':404,
            'title':'Not found',
            'msg':'Invalid page the page you are trying to access does not exist'
        }
        return make_response(render_template('error.html',error=error),404)
# Route leading to home page
@app.route("/")
def index(page=1):
    g.len = len
    g.addMarkup = lambda x: x

    books = db.execute(
        'SELECT '
            ' * '
        'FROM ('
                'SELECT '
                    'isbn,title,author,year,average_rating,reviews_count,'
                    'ROW_NUMBER () OVER ( '
                                        'ORDER BY average_rating DESC'
                                        ') FROM books'
            ') X'
        ' WHERE ROW_NUMBER BETWEEN :low AND :high',
        {
        'low':(page-1)*12+1,
        'high':page*12
        }
    ).fetchall()
    if not books and page != 1:
        error404()
    return render_template('index.html', title='Home', page=page, books=books)

app.add_url_rule('/page/<int:page>','index',index)

@app.route("/search")
@login_required
def search(page=1):
    g.len = len
    item = request.args.get('item',None).strip()
    error = None
    if item is None:
        error = {
            'code':400,
            'title':'Bad request',
            'msg':'Search item missing please include search item in url'
        }
        return make_response(render_template('error.html',error=error),400)

    g.addMarkup = lambda x: Markup(x.replace(item,f"<mark>{item}</mark>"))
    books = db.execute(
        'SELECT '
            '* '
        'FROM ( '
                'SELECT '
                    'isbn,title,author,year,average_rating,reviews_count, '
                    'ROW_NUMBER () OVER ( '
                                        'ORDER BY title '
                                        ') FROM books '
                    'WHERE isbn = :item OR title ILIKE :iteml OR author ILIKE :iteml '
            ') X '
        'WHERE ROW_NUMBER BETWEEN :low AND :high ',
        {
            'item' : item,
            'iteml':f'%{item}%',
            'low':(page-1)*12+1,
            'high':page*12
        }
    ).fetchall()
    if not books and page != 1:
        error404()

    return render_template('search.html',title='Search', page=page, item=item, books=books)

app.add_url_rule('/search/page/<int:page>','search',search)

@app.route('/register',methods=['GET','POST'])
def register():
    msg = None
    if request.method == 'POST':
        username = request.form.get('username',None).strip()
        password = request.form.get('password',None).strip()

        if username!='' and password!='':
            user = db.execute(
                'SELECT * FROM users WHERE username=:username',
                {
                    'username': username
                }
            ).fetchone()

            if user is not None:
                msg = {'class':'danger','body':f'Username "{username}" already exist, please choose diffrent username or click on login page.'}
            if msg is None:
                db.execute(
                    'INSERT INTO users (username, password) values (:username, :password)',
                    {
                    'username':username,
                    'password': generate_password_hash(password)
                    }
                )
                db.commit()
                return redirect(url_for('login'))

    hrefs = Markup(f"""<small>Already a user?, <a href={url_for('login')}>Log in</a> here</small>""")

    return render_template('forms.html', title='Register', msg=msg, hrefs=hrefs)

@app.route("/login",methods=['GET','POST'])
def login():
    msg = None

    if request.method == 'POST':
        username = request.form.get('username',None).strip()
        password = request.form.get('password',None).strip()

        if username!='' and password!='':
            user = db.execute(
                'SELECT * FROM users WHERE username=:username',
                {
                    'username': username
                }
            ).fetchone()
            if user is not None:
                if not check_password_hash(user.password,password):
                    msg = {'class':'danger','body': 'Password Incorrect'}
                if msg is None:
                    session['user_id'] = user.id
                    flash('You were successfully logged in')
                    return redirect(url_for('index'))
            else:
                msg = {'class':'danger','body': f'"{username}" Incorrect username, If not registerd, please register before trying to login'}

    hrefs = Markup(f"""<small>Don't have account, <a href={ url_for('register') }>Register</a> here</small>""")

    return render_template('forms.html', title='Login', msg=msg, hrefs=hrefs)

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash('You were successfully logged out')
    return redirect(url_for('index'))


@app.route('/book/<string:isbn>')
def book(isbn):
    g.len = len
    g.addMarkup = lambda x:x
    book = db.execute(
        'SELECT * FROM books '
        'WHERE isbn=:isbn',
        {
        'isbn':isbn
        }
    ).fetchone()

    if book is None:
        error404()

    reviews = db.execute(
        'SELECT * FROM reviews '
        'WHERE book_id = :id ',
        {
        'id':book.id
        }
    ).fetchall()

    reviews = { i:i.username for i in reviews}

    return render_template('book.html', title=book.title , book=book, reviews=reviews)

@app.route('/post/<string:isbn>',methods=["POST"])
@login_required
def post_review(isbn):
    rating = request.form.get('rating').strip()
    text_review = request.form.get('text_review').strip()
    book = db.execute(
        'SELECT * FROM '
        'books '
        'WHERE isbn = :isbn ',
        { 'isbn': isbn }
    ).fetchone()

    if not book or int(rating) not in range(1,6):
        error = {
            'code':422,
            'title':'Invalid data',
            'msg': "Please submit valid data"
        }
        return make_response(render_template('error.html',error=error),422)
    review = db.execute(
        'SELECT * FROM '
        'reviews '
        'WHERE username = :username and book_id = :book_id',
        {
            'username':g.user.username,
            'book_id':book.id
        }
    ).fetchone()
    if review is not None:
        error = {
            'code':403,
            'title':'Not Allowed',
            'msg': 'You are not allowed to review same book twice'
        }
        return make_response(render_template('error.html',error=error),403)

    if rating and text_review:
        db.execute(
            'INSERT INTO reviews '
            '( username, book_id, rating, text_review) '
            'VALUES ( :username, :book_id, :rating, :text_review) ',
            {
                'username': g.user.username,
                'book_id' : book.id,
                'rating'  : rating,
                'text_review' : text_review
            }
        )
        db.commit()
    return redirect(url_for('book',isbn=isbn))

@app.route('/api/<string:isbn>')
def book_info(isbn):
    book = db.execute(
        'SELECT * '
        'FROM books '
        'WHERE isbn = :isbn ',
        {
        'isbn' : isbn
        }
    ).fetchone()
    if book is None:
        return make_response(jsonify(status_code=404,message="Data doesn'd exist"),404)

    res  = jsonify(
        title = book.title,
        author = book.author,
        year = book.year,
        isbn = book.isbn,
        review_count = book.reviews_count,
        average_score = book.average_rating
    )

    return make_response(res,200)
