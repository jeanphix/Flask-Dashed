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


Dealing with security
---------------------

securing specific all module endpoints::

    from flask import session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')

    @book_module.secure_path('.', http_code=401)
    def login_required():
        return "user" in session

securing specific module endpoint::

    @book_module.secure_path('list', http_code=403)
    def check_list_credential():
        # I'm now signed in, may I access the ressource?
        return session.user.can_list()


SQLALchemy extension
--------------------

code::

    from flask_dashed.ext.sqlalchemy import ModelAdminModule


    class BookModule(ModelAdminModule):
        model = Book
        db_session = db.session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')
