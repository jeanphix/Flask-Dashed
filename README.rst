Installation
------------

    pip install -e git+git://github.com/jean-philippe/Flask-Dashed.git#egg=Flask-Dashed
    cd Flask-Dashed
    python setup.py install


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

Securing all admin endpoints::

    from flask import session

    @admin.secure_endpoint('.', http_code=401)
    def login_required():
        return "user" in session

Securing all module endpoints::

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')

    @book_module.secure_endpoint('.', http_code=401)
    def login_required():
        return "user" in session

Securing specific module endpoint::

    @book_module.secure_endpoint('list', http_code=403)
    def check_list_credential():
        # I'm now signed in, may I access the ressource?
        return session.user.can_list()


SQLALchemy extension
--------------------

Code::

    from flask_dashed.ext.sqlalchemy import ModelAdminModule


    class BookModule(ModelAdminModule):
        model = Book
        db_session = db.session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')
