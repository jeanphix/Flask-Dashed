Installation
------------

    pip install Flask-Dashed


Minimal usage
-------------

code::

    from flask import Flask
    from flask_dashed.admin import Admin

    app = Flask(__name__)
    admin = Admin(app)

    if __name__ == '__main__':
        app.run()





SQLALchemy extension
--------------------

code::

    from flask_dashed.ext.sqlalchemy import ModelAdminModule


    class BookModule(ModelAdminModule):
        model = Book
        db_session = db.session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')


Dealing with security
---------------------

securing specific module endpoint::

    from flask import session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')

    @book_module.secure_endpoint('list', [http_code=403])
    def secure_list():
        return "user" in session