import os
from functools import wraps

from flask import Flask, session, request, render_template, url_for, redirect, g, make_response,flash
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SECRET_KEY"] = 'secret'
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
            flash("Please login to use 'Search' function")
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
        print(g.user.username)


# Route leading to home page
@app.route("/")
def index(page=1):
    g.len = len
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
        error = {
            'code':404,
            'title':'Not found',
            'msg':'Invalid page the page you are trying to access does not exist'
        }
        return make_response(render_template('error.html',error=error),404)

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
    return render_template('register.html', title='Register', msg=msg)

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

    return render_template('login.html', title='Login', msg = msg)

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash('You were successfully logged out')
    return redirect(url_for('index'))
