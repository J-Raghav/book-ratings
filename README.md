# Book Ratings

##  **File: import.py**

### functions

- **create\_tables**

    - Input  : SCHEMA.sql ( for basic table structure )
    - Output : Generate table present in SCHEMA.sql

- **get\_books\_data** ( generator function)

    - Input  : books.csv ( for list of isbn required for API request)
    - Output : yields  information about books fetched from GOODREADS API  

- **insert\_books**

    - Input  : Uses book data yielded by **get\_books\_data**
    - Output : Inserts book data in Database at heroku

## **File: application.py**

### View\_Functions

- **index(page=1)**    :
  - Path = [ _'/'_ ,  _'/page/<int:page>'_ ]  
  - Returns  _index.html_  page.
- **search(page=1)**   :
  - Path = [ _'/search'_ , _'/search/page/<int:page>'_ ]
  - Returns _search.html_ page or Redirects to _login_ view function.
- **register()**         :
  - Path = _'/register'_
  - Returns _forms.html_ page or Redirects to _login_ view function.
- **login()**            :
  - Path = _'/login'_  
  - Returns _forms.html_ page.
- **logout()**           :
  - Path =  _'/logout'_  
  - Redirects to  _index_ view function.
- **book(isbn)**       :
  - Path =  _'/book/<string:isbn>'_  
  - Returns _book.html_ page.
- **post\_reviews()**    :
  - Path =  _'/post'_  
  - Redirects _book_ view function.
- **book\_info(isbn)** :
  - Path = _'/api/<string:isbn>'_  
  - Returns **JSON response**.

### Other Functions

- **load\_loggedin\_user()** - loads logged in user if any. ( called before every request )
- **login\_required(view)**      - protects routes which require authorization. ( called before any protected view )
  Protected Views - [ 'search', 'post_review' ]

## **Dir: Templates**

- **macros.html**        - Contains macros used as module only.
  - _card(book, flag=True)_ : Used in **book.html**
  - _form(title, hrefs, msg)_ : Used in **forms.html**
  - _paginateBooks(endpoint, books, page, item=None)_ : Used in **search.html** and **index.html**

- **layout.html**        - Contains basic layout used as base for all pages.   
- **index.html**         - Home page
- **forms.html**         - Register and Login pages  
- **search.html**        - Search result page
- **book.html**          - Book page
- **error.html**         - Error page

## **Dir: Static**

- **master.css**         - Contains styles for all pages.


## **Other Files**

- **books.csv**          : Contains basic information about 5000 books used to get data about books in **import.py**.
- **requirements.txt**  : Contains requirements of project meant o be installed by **pip install -r requirements.txt**.
- **runtime.txt**       : Contains python runtime required for deployment to heroku.
- **Procfile**          : Contains init info for deployment to heroku.
