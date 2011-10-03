Introduction
------------

Flask-Dashed provides tools for build simple and extensible admin interfaces.


.. image:: https://github.com/jean-philippe/Flask-Dashed/raw/master/docs/_static/screen.png



Installation
------------

    pip install -e git+git://github.com/jean-philippe/Flask-Dashed.git#egg=Flask-Dashed


Minimal usage
-------------

Code::

    from flask import Flask
    from flask_dashed.admin import Admin

    app = Flask(__name__)
    admin = Admin(app)

    if __name__ == '__main__':
        app.run()


Dealing with security
---------------------

Securing all module endpoints::

    from flask import session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')

    @book_module.secure(http_code=401)
    def login_required():
        return "user" in session

Securing specific module endpoint::

    @book_module.secure_endpoint('edit', http_code=403)
    def check_edit_credential(view):
        # I'm now signed in, may I modify the ressource?
        return session.user.can_edit_book(view.object)


SQLALchemy extension
--------------------

Code::

    from flask_dashed.ext.sqlalchemy import ModelAdminModule


    class BookModule(ModelAdminModule):
        model = Book
        db_session = db.session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')
