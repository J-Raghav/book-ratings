# Book Ratings

##  **import.py**

### functions

- _create\_tables_

    - Input  : SCHEMA.sql ( for basic table structure )
    - Output : Generate table present in SCHEMA.sql

- _get\_books\_data_ ( generator function)

    - Input  : books.csv ( for list of isbn required for API request)
    - Output : yields  information about books fetched from GOODREADS API  

- _insert\_books_

    - Input  : Uses book data yielded by **get\_books\_data**
    - Output : Inserts book data in Database at heroku

## **application.py**

### view\_functions

- _index(page=1)_      - Attached with ( _'/'_ ) and ( _'/page/<int:page>'_ ) routes yields HOME( _index.html_ ) page.
- _search(page=1)_     - Attached with ( _'/search'_ ) and (_'/search/page/<int:page>'_) route yields SEARCH( _search.html_ ) page.
- _register_           - Attached with ( _'/register'_ ) route yields register( _form.html_ ) page.
- _login_              - Attached with ( _'/login'_ ) route yields login( _forms.html_ ) page.
- _logout_             - Attached with ( _'/logout'_ ) route redirects to _index_ view function.
- _book(isbn)_         - Attached with ( _'/book/<string:isbn>'_) route yields book( _book.html_ ) page.
- _post\_reviews_      - Attached with ( _'/post'_ ) route redirects to _index_ view function.
- _book\_info(isbn)_   - Attached with ( _'/api/<string:isbn>'_) route and returns **JSON response**.

### functions

- _load\_loggedin\_user_ - loads logged in user if any. ( called before every request )
- _login\_required_      - protects routes which require authorization. ( called before any protected view )
  Protected Views - [ 'search', 'post_review']

## **Templates**

- _macros.html_        - Contains macros used as module only.
  - _card(book, flag=True)_ : Used in **book.html**
  - _form(title, hrefs, msg)_ : Used in **forms.html**
  - _paginateBooks(endpoint, books, page, item=None)_ : Used in **search.html** and **index.html**

- _layout.html_        - Contains basic layout used as base for all pages.   
- _index.html_         - Home page
- _forms.html_         - Register and Login pages  
- _search.html_        - Search result page
- _book.html_          - Book page
- _error.html_         - Error page

## **static**

- _master.css_         - Contains styles for all pages.


## **Other Files**

- _books.csv_         : Contains basic information about 5000 books used to get data about books in **import.py**.
- _requirements.txt_  : Contains requirements of project meant o be installed by **pip install -r requirements.txt**.
- _runtime.txt_       : Contains python runtime required for deployment to heroku.
- _Procfile_          : Contains init info for deployment to heroku.
